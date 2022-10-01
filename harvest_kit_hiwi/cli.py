"""Console script for harvest_kit_hiwi."""
import os
import sys
import click
import json
import datetime
from collections import defaultdict

import cairosvg

from harvest_kit_hiwi.util import get_version
from harvest_kit_hiwi.util import MONTH_NAMES
from harvest_kit_hiwi.config import CONFIG
from harvest_kit_hiwi.harvest import HarvestApi
from harvest_kit_hiwi.processing import TimeSpan, ArbeitszeitData
from harvest_kit_hiwi.document import create_azd_svg


@click.group('hhiwi', invoke_without_command=True)
@click.option('--version')
def cli(version):

    if version:
        click.secho(get_version())
        return 0


@click.command('azd', short_help='Creates the PDF document for the Arbeitszeitdokumentation')
@click.argument('month', type=click.Choice([str(k) for k in MONTH_NAMES.keys()]))
@click.option('--year', type=click.INT, default=datetime.datetime.now().year,
              help='The year for which to render the monthly documentation')
@click.option('-a', '--archive-path', type=click.Path(), default='./azd_archive',
              help='The path to the folder that contains the archive of past Arbeitszeit data')
@click.option('-n', '--non-archival', is_flag=True,
              help='Do not save the created AZD data to the archive')
def azd(month: str,
        year: int,
        archive_path: str,
        non_archival: bool):
    click.secho('Generating "KIT Arbeitszeitdokumentation" from Harvest Time Tracking...')
    year = str(year)

    # -- RETRIEVAL --
    # First thing we need to do is establish a connection to Harvest to retrieve the raw data.
    try:
        api = HarvestApi(
            url=CONFIG.get_harvest_url(),
            account_id=CONFIG.get_harvest_id(),
            account_token=CONFIG.get_harvest_token()
        )
        time_entries = api.get_time_entries(
            project_id=CONFIG.get_harvest_project_id()
        )
        click.secho(f'retrieved {len(time_entries)} time entries from harvest')

    except Exception as e:
        click.secho(str(e), fg='red')
        return 1

    # -- ARCHIVE --
    archive = {}
    dt = datetime.datetime(month=int(month), year=int(year), day=10)
    dt_prev = dt - datetime.timedelta(days=30)
    prev_key = (dt_prev.month, dt_prev.year)
    if os.path.exists(archive_path) and os.path.isdir(archive_path):
        files = os.listdir(archive_path)
        click.secho(f'discovered archive with {len(files)} entries')

        for file in files:
            file_path = os.path.join(archive_path, file)
            if file.endswith('.json'):
                with open(file_path, mode='r') as file:
                    data = json.load(file)
                    azd_data = ArbeitszeitData.from_dict(data)
                    archive[(azd_data.month, azd_data.year)] = azd_data

    else:
        click.secho(f'archive not found')

    # -- PROCESSING --
    # Then we need to process these raw time entries into TimeSpan objects, which we can perform processing
    # on more easily
    time_spans = [TimeSpan.from_time_entry(time_entry) for time_entry in time_entries]
    total_time_delta = datetime.timedelta(hours=0)
    leave = 0

    # (1) The first thing we have to do is filter all those entries to only have the ones for the selected
    # month
    time_spans = [ts for ts in time_spans if str(ts.start_datetime.month) == month]

    # (2) This first additional processing step optionally merges all time spans that are recorded on the
    # same day into a single one.
    if CONFIG.do_merge_daily():
        day_map = defaultdict(list)
        for ts in time_spans:
            day = ts.start_datetime.day
            day_map[day].append(ts)

        # And then we simply merge all the dicts
        time_spans = [sum(time_spans_sorted[1:], time_spans_sorted[0])
                      for time_spans in day_map.values()
                      if (time_spans_sorted := sorted(time_spans, key=lambda ts: ts.start_datetime))]

    # (3) Another optional processing step is the automatic adding of leave time. There is a certain amount
    # of monthly leave that every hiwi has available and which SHOULD be used up completely. One good way
    # to do this is just to "pretend" to use the exactly right amount every month
    if CONFIG.do_monthly_leave():
        leave = CONFIG.get_monthly_leave()

    # (4) Another problem is the handling of the carry over between months. It's really easy to lose track
    # which is why it's possible to clip all the overtime of a month and artificially make it such that
    # it fits perfectly
    for ts in time_spans:
        total_time_delta += ts.time_delta

    total_working_seconds = int(CONFIG.get_working_hours() * 3600)
    total_difference_minutes = total_time_delta.total_seconds() - total_working_seconds - leave * 3600
    if CONFIG.do_clip_hours() and total_difference_minutes > 0:
        # To do this we will simply remove an equal amount of time from all the currently registered
        # time spans
        individual_remove_minutes = int(total_difference_minutes / len(time_spans))
        for ts in time_spans:
            ts.modify_end(-individual_remove_minutes * 60)

    carry_over = -total_difference_minutes
    click.secho(f'calculated carry over of {carry_over:.2f} seconds ({carry_over / 3600:.2f} hrs)')

    # Finally, we need to order this list by the starting time to list the time spans in chronological
    # order in the final document
    time_spans = sorted(time_spans, key=lambda ts: ts.start_datetime)

    # -- RENDERING --
    # We will output the raw svg file as well as the pdf. This is so that the user can potentially make
    # manual adjustments on the svg file and then render it as pdf afterwards manually as well.
    svg_path = os.path.join(os.getcwd(), f'azd_{month}_{year}.svg')
    pdf_path = os.path.join(os.getcwd(), f'azd_{month}_{year}.pdf')

    # Now for the actual rendering to take place we first need to wrap all the relevant data into a
    # "AbeitszeitData" object. This will wrap the static personal information as well as the list of time
    # spans.
    carry_over = 0
    if prev_key in archive:
        azd_prev = archive[prev_key]
        carry_over = azd_prev.carry_over_after

    azd_data = ArbeitszeitData(
        time_spans=time_spans,
        name=CONFIG.get_name(),
        personnel_number=CONFIG.get_personnel_number(),
        institute=CONFIG.get_institute(),
        working_hours=CONFIG.get_working_hours(),
        hourly_rate=CONFIG.get_hourly_rate(),
        carry_over=carry_over,
        leave=leave,
        month=month,
        year=year,
    )

    create_azd_svg(
        azd_data=azd_data,
        output_path=svg_path
    )

    with open(svg_path, mode='rb') as svg_file, open(pdf_path, mode='wb') as pdf_file:
        svg_content = svg_file.read()
        pdf_content = cairosvg.svg2pdf(svg_content)
        pdf_file.write(pdf_content)
        click.secho(f'wrote output pdf: "{pdf_path}"')

    if not non_archival:
        # The archive path might not exist
        if not os.path.exists(archive_path):
            os.mkdir(archive_path)

        data = azd_data.to_dict()
        json_path = os.path.join(archive_path, f'{year}_{month}.json')
        with open(json_path, mode='w') as file:
            json.dump(data, file, indent=4)
            click.secho(f'wrote archive: "{json_path}"')


cli.add_command(azd)

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
