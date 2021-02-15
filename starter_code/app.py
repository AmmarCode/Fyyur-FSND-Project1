#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
from datetime import datetime
from logging import FileHandler, Formatter

import babel
import dateutil.parser
import psycopg2
from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form

from forms import *
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []

    # Retrive all venues
    venues = Venue.query.all()

    # Use set to prevent duplicate venues
    locations = set()

    for venue in venues:
        # add city/state tuples
        locations.add((venue.city, venue.state))

    # add venues for each city/state
    for location in locations:
        data.append({
            "city": location[0],
            "state": location[1],
            "venues": []
        })

    for venue in venues:
        num_upcoming_events = 0

        events = Event.query.filter_by(venue_id=venue.id).all()

        # filter num_upcoming_events by getting current date
        current_date = datetime.now()

        for event in events:
            if event.start_time > current_date:
                num_upcoming_events += 1

        for venue_location in data:
            if (venue.state == venue_location['state'] and 
                venue.city == venue_location['city']):
                venue_location['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_events": num_upcoming_events
                })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

    response = {
        "count": result.count(),
        "data": result
    }
    return render_template('pages/search_venues.html',
                           results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def event_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    events = Event.query.filter_by(venue_id=venue_id).all()
    past_events = []
    upcoming_events = []
    current_time = datetime.now()

    for event in events:
        data = {
            "speaker_id": event.speaker_id,
            "speaker_name": event.speaker.name,
            "speaker_image_link": event.speaker.image_link,
            "start_time": format_datetime(str(event.start_time))
        }
        if event.start_time > current_time:
            upcoming_events.append(data)
        else:
            past_events.append(data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "image_link": venue.image_link,
        "facebook_link": venue.facebook_link,
        "website": venue.website,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "past_events": past_events,
        "upcoming_events": upcoming_events,
        "past_events_count": len(past_events),
        "upcoming_events_count": len(upcoming_events)
    }

    return render_template('pages/event_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        form = VenueForm()
        venue = Venue(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      address=form.address.data,
                      phone=form.phone.data,
                      image_link=form.image_link.data,
                      website=form.website.data,
                      facebook_link=form.facebook_link.data,
                      seeking_talent=form.seeking_talent.data,
                      seeking_description=form.seeking_description.data,
                      )

        db.session.add(venue)
        db.session.commit()
    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + 
              ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        venue_name = venue.name

        db.session.delete(venue)
        db.session.commit()

        flash('Venue ' + venue_name + ' was deleted')
    except:
        flash('an error occured and Venue ' + venue_name + ' was not deleted')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Speakers
#  ----------------------------------------------------------------


@app.route('/speakers')
def speakers():
    # TODO: replace with real data returned from querying the database
    data = []

    speakers = Speaker.query.all()

    for speaker in speakers:
        data.append({
            "id": speaker.id,
            "name": speaker.name
        })
    return render_template('pages/speakers.html', speakers=data)


@app.route('/speakers/search', methods=['POST'])
def search_speakers():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    search_term = request.form.get('search_term', '')

    result = Speaker.query.filter(Speaker.name.ilike(f'%{search_term}%'))

    response = {
        "count": result.count(),
        "data": result
    }

    return render_template('pages/search_speakers.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/speakers/<int:speaker_id>')
def event_speaker(speaker_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    speaker = Speaker.query.get(speaker_id)
    events = Event.query.filter_by(speaker_id=speaker_id).all()
    past_events = []
    upcoming_events = []
    current_time = datetime.now()

    for event in events:
        data = {
            "venue_id": event.venue_id,
            "venue_name": event.venue.name,
            "venue_image_link": event.venue.image_link,
            "start_time": format_datetime(str(event.start_time))
        }
        if event.start_time > current_time:
            upcoming_events.append(data)
        else:
            past_events.append(data)

    data = {
        "id": speaker.id,
        "name": speaker.name,
        "city": speaker.city,
        "state": speaker.state,
        "phone": speaker.phone,
        "image_link": speaker.image_link,
        "facebook_link": speaker.facebook_link,
        "website": speaker.website,
        "seeking_venue": speaker.seeking_venue,
        "seeking_description": speaker.seeking_description,
        "past_shows": past_events,
        "upcoming_shows": upcoming_events,
        "past_shows_count": len(past_events),
        "upcoming_shows_count": len(upcoming_events)
    }

    return render_template('pages/event_speaker.html', speaker=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/speakers/<int:speaker_id>/edit', methods=['GET'])
def edit_speaker(speaker_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    form = SpeakerForm()

    speaker = Speaker.query.get(speaker_id)

    speaker_data = {
        "id": speaker.id,
        "name": speaker.name,
        "city": speaker.city,
        "state": speaker.state,
        "phone": speaker.phone,
        "website": speaker.website,
        "facebook_link": speaker.facebook_link,
        "seeking_venue": speaker.seeking_venue,
        "seeking_description": speaker.seeking_description,
        "image_link": speaker.image_link
    }

    return render_template('forms/edit_speaker.html',
                           form=form, speaker=speaker_data)


@app.route('/speakers/<int:speaker_id>/edit', methods=['POST'])
def edit_speaker_submission(speaker_id):
    # TODO: take values from the form submitted, and update existing
    # speaker record with ID <speaker_id> using the new attributes
    try:
        form = SpeakerForm()

        speaker = Speaker.query.get(speaker_id)
        name = form.name.data

        speaker.name = name
        speaker.phone = form.phone.data
        speaker.city = form.city.data
        speaker.state = form.state.data
        speaker.image_link = form.image_link.data
        speaker.facebook_link = form.facebook_link.data
        speaker.website = form.website.data
        speaker.seeking_venue = form.seeking_venue.data
        speaker.seeking_description = form.seeking_description.data

        db.session.commit()
        flash('The Speaker ' + name + ' has been successfully updated!')
    except:
        db.session.rolback()
        flash('An Error has occured and the update unsuccessful')
    finally:
        db.session.close()

    return redirect(url_for('event_speaker', speaker_id=speaker_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        name = form.name.data

        venue.name = name
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.website = form.website.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data

        db.session.commit()
        flash('Venue ' + name + ' has been updated')
    except:
        db.session.rollback()
        flash('An error occured while trying to update Venue')
    finally:
        db.session.close()
    return redirect(url_for('event_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/speakers/create', methods=['GET'])
def create_speaker_form():
    form = SpeakerForm()
    return render_template('forms/new_speaker.html', form=form)


@app.route('/speakers/create', methods=['POST'])
def create_speaker_submission():

    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        form = SpeakerForm()

        speaker = Speaker(name=form.name.data, 
                        city=form.city.data, 
                        state=form.city.data,
                        phone=form.phone.data, 
                        image_link=form.image_link.data, 
                        facebook_link=form.facebook_link.data)

        db.session.add(speaker)
        db.session.commit()
        # on successful db insert, flash success
        flash('Speaker ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. Speaker ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/speaker/<int:speaker_id>', methods=['DELETE'])
def delete_speaker(speaker_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        speaker = Speaker.query.get(speaker_id)
        speaker_name = speaker.name

        db.session.delete(speaker)
        db.session.commit()

        flash('Speaker ' + speaker_name + ' was deleted')
    except:
        flash('an error occured and Speaker ' +
              speaker_name + ' was not deleted')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/events')
def events():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    events = Event.query.order_by(db.desc(Event.start_time))

    data = []

    for event in events:
        data.append({
            "venue_id": event.venue_id,
            "venue_name": event.venue.name,
            "speaker_id": event.speaker_id,
            "speaker_name": event.speaker.name,
            "speaker_image_link": event.speaker.image_link,
            "start_time": format_datetime(str(event.start_time))
        })
    return render_template('pages/events.html', events=data)


@app.route('/events/create')
def create_events():
    # renders form. do not touch.
    form = EventForm()
    return render_template('forms/new_event.html', form=form)


@app.route('/events/create', methods=['POST'])
def create_event_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        event = Event(speaker_id=request.form['speaker_id'], 
                    venue_id=request.form['venue_id'],
                    start_time=request.form['start_time'])

        db.session.add(event)
        db.session.commit()
    # on successful db insert, flash success
        flash('Event was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. Event could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
