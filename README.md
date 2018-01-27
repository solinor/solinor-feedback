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
