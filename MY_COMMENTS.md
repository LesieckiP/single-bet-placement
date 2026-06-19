What i want to add:
- schema validation for rest (pydantic)
- test case for past game
- test case for simultaneous api request for bet


## When and why i used AI within this task
1. Test Plan generation
    Created workspace within Claude Cowork with instructions for the agent that clarified it's role for the project. File with specification was uploaded. this allows me to use it in future in case i will have to keep the same rules and behavior for same topic.
    Used AI because it will generate structure and some content much faster than human and can easily be guided to use specific practices (like ISTQB and ISO). Afterwards it was **heavily** reviewed by me and i get rid of few parts also structured it to the way i see it right. Done proper test cases refinement and prioritized them as asked in the task.
    Creation of such test plan is not every-day task, it's rather being created at the beginning (being updated as the timeline progresses) and during specific phases. Also having such detailed requirement written as a whole is not commonly seen in modern software development. I have came across more atomic user stories than such detailed specification especially in web and app design projects (in automotive and networking devices the approach "slightly" differ) so i treated this part of task more like an excercise to show my knowledge about testing practices and understandment of it.
2. Some of the nuances clarification - rounding in sports betting as i noiced that the app was rounding up (ex. 2.5 × 2.45 = 6.125 but in app it is 5.13). This helped me to understand the practice in the bussiness.
3. Re-Used project from step #1 it to prepare bug report file based on the list of issues i found during my exploratory testing session. For full transparency i pasted the prompt into the [BUGREPORT_PROMPT.md](./part_a/BUGREPORT_PROMPT.md). 
    Afterwards i have carefully reviewed the result, fixed steps, expected and actual values against the requirements and re-prioritised the issues slightly (as this part actually were done pretty decent). This gave me confidence all my issues were **correctly** addressed. During review i have added attachments to the bugs. Why AI here? - It saved me a lot of time of typing the same strings especially when the fields were already defined in the task. I wanted to use it just to prepare me a basic structure while giving future reviewers (you) visibility if i understood the requirements while finding issues.

# In Test Automation:
1. Used for help with handling the proper error handling in requests (for example 401 and 405 response difference, the implementation is done in base_endpoint.py file )
2. Expanding the patterns introduced - after setting up models for responses i asked it to create next models for me, example prompt:
```
Create pydantic model for the bet_models.py file similar to other models already created, you can see matches_models.py as reference. Below im providing you with the schema:
PlaceBetResponse{
message	string
example: Bet placed successfully
matchId	string
example: premier-league-manutd-chelsea
selection	string
example: HOME
stake	number
example: 10
odds	number
example: 2.45
payout	number
example: 24.5
balance	number
example: 115.5
currency	string
example: EUR
}
```
3. Write some regexps in pageObjects

### Model used: Sonnet 4.6 (medium effort)

## How i was not using AI in the task:
1. I was not using it to test the app (neither for UI nor for API)
2. I was not using it to ask about ideas of proper approach to this recruitment task
3. I was not uploading images of the UI to verify it for me against the requirements in the document recieved.


## Why i selected this particular Test Cases in the Test Plan:
Focused on critical functionality (money leaks prevention) and posibility to make the actuall bet (money earnings), treated UI issues with lower priority, examples (if proper fields are displayed). If there is workaround possible like page refresh the priority was also lowered by me.
