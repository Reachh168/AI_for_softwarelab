# Lab notes

*Fill this in as you go — it's part of your submission (Lab 0).*
 - copy API Key from GROQ and Paste it into .env file 
 - run following command  -  python -m venv venv
                                   - source venv/bin/activate
                                   - pip install -r requirements.txt
 - run Single Question and exit
 - do some question testing using diffrent temp version.
 
## Statelessness
What happened when you sent only the latest message vs. the full history?
 - when sent only latest message, the bot forgot the previous conversation.
 - when sent full history, the bot remembered the previous conversation.

## Temperature
How did `--temp 0.2` compare to `--temp 1.3` on the same prompt?
- between temp 0.2 and temp 1.3 there is not much difference, on 0.2 answer is more highly probable words. The output is focused, deterministic, and highly consistent, and on 1.3 answer is less probable words, leading to more creative, diverse, and unexpected responses.

## Tokens
What did you notice about token counts as prompts got longer?
- the token count increased as the prompt length increased and it take long time to process

## Anything that surprised you or broke
- it amaze how language model can understand context and give me an understandable answer.
