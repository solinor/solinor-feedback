# Solinor Feedback

This is a simple tool to facilitate feedback between colleagues. This is not meant to be off-the-shelf solution. Manual setup and tinkering is required to get everything work properly.

- This is a quick one-off solution, not a finished or polished product.
- Forms are outsourced to Google Forms. Some values are hardcoded on the code, such as "the first question is whether feedback is anonymous or not". See `views.py:record_response` method for more details.

Master branch of [this repository](https://github.com/solinor/solinor-feedback) is automatically deployed to Solinor's internal service.

## Process for giving and receiving the feedback

1. Everyone requests feedback from relevant people (see `/ask_for_feedback` URL)
2. After that is done (or continually; based on past experience dedicating a specific time for everyone works better), everyone writes feedback for the requests they received.
3. Everyone has 1-on-1 meeting with another person (mentor / supervisor / similar) to go through the feedback they received. On that session there is time to discuss the feedback, further actions etc.
4. After the meeting, feedbacks are released, and available through the web interface for directly to the recipient.


## Anonymous feedback

When giving feedback, there is an option to decide whether feedback is anonymous or not to the recipient. Feedback is rarely truly anonymous - most of the time recipient can guess who gave the feedback, if it includes any practical examples or details.

In case of anonymous feedback, recipient will not see the name, _but_ mentor can see it if need be: for example, asking clarifications, reacting to abusive or insulting feedback etc. It is important to make a difference between insults and constructive criticism.


# Setting up

## Google Forms

Create three different (or duplicate, if that is what you want) forms:

- full form for those who are responding to feedback request.
- simpler for those who just want to send some feedback to people who did not request feedback.
- for external users - does not require signing in, does not ask internal questions, and use relevant terminology.

Require signing in and record respondent's email addresses for first two forms. For form title, question titles and question descriptions, use '<name>' placeholder for respondents.

Create a new, empty Drive folder.

Open [script.google.com](https://script.google.com), and create two new scripts: [send-feedback](google-apps-scripts/send-feedback.gscript) and [copy-feedback-forms](google-apps-scripts/copy-feedback-forms.gscript). Copy IDs from all four items created above to `copy-feedback-forms` fields. Set `domain` and `sharedSecret` variables.

There is annoying limitation of max 20 triggers per script. You will need to make enough copies of `send-feedback` script (ceil(number of users * 3 / 20)).


## Configure Django app to Heroku (or any other platform)

- Hobby or free PostgreSQL database.
- Environment variables: `RESPONSE_SHARED_SECRET` from previous step, `SECRET`, and G Suite authentication options (see the next section).

*Heroku buildpacks*

- heroku/python
- https://github.com/ojarva/django-compressor-heroku-buildpack.git

## G Suite integration

G Suite is used for signing in. Steps to setup:

- Go to https://console.cloud.google.com/
- Create a new project
- Go to "APIs & Services", enable "Google+ API". No need to configure Google+.
- Go to "APIs & Services -> Credentials". Create OAuth Client ID. Select Web Application. Don't set "Authorised JavaScript origins". Set "Authorised redirect URIs" to your application's install address.
- Copy access key, secret key. Set to `GOOGLEAUTH_CLIENT_ID` and `GOOGLEAUTH_CLIENT_SECRET` variables.
- Set `GOOGLEAUTH_CALLBACK_DOMAIN` to one of the addresses you entered to "Authorized redirect URIs".
- Set `GOOGLEAUTH_APPS_DOMAIN` to your G Suite domain to restrict others from signing in.

## Sync users

There is no automated mechanism to sync users. Write a short script to parse whatever user list you have, and insert users to `feedback.User`

## Create forms in Google Scripts

Run `copy-feedback-forms` until all forms are created.

## Attach triggers

Run each `send-feedback` script with `attachToForms` entrypoint to attach scripts to forms.
