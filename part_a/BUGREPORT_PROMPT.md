As a tester i have checked the sports betting app under during exploratory session:
https://qae-assignment-tau.vercel.app/?user-id=candidate-LfzI2CKDRw
App allows to place a single bet.
I got multiple issues to report and some improvements. I want you to put my list in the format, do this as a senior QA engineer:
Bug ID & Title
Severity: Critical / High / Medium / Low
Reproduction Steps
Expected vs Actual result
Business Impact: Brief sentence on user/business consequence
Evidence: Screenshot or brief note

If you don't understand the point from the list or If you are not sure what to put into one of the fields - ask for clarification. You can try to decide on Severity by yourself but if not sure also ask. Put the list of bugs from most importants to least and then improvement suggestions last. 
For putting the steps together you can use the images from the app (attached) one is without Bet Slip and second one is having a Bet Slip visible after selecting a bet. Note that first image is directly what user sees after opening provided URL. Use them as a help to provide the reproduction steps. Do not try to suggest any new bugs based on that. Put this into the .md file. Allow the posibility to attach images from the issues.

Here is the list of issues:
1. sorting - i see february, march and then feb again and then march and februrary
2. MLS game - Inter Miami vs LAFC got no exact date displayed (Inter Miami - LAFC) just "Saturday" but the payload from request is having a kickoffDate:
    {
        "id": "mls-inter-miami-lafc-2026-06-20",
        "competition": "MLS",
        "kickoffDate": "2026-06-20",
        "homeTeam": "Inter Miami",
        "awayTeam": "LAFC",
        "odds": {
            "home": 2.65,
            "draw": 3.45,
            "away": 2.45
        }
    }
3. Lower odds filter does not work correctly. When i selected filter to the exactly same value that is the odd "1" (from home team) then this record disappears but when i select 0.01 greater or higher then it shows again (and it should because odds X and 2 are greater)
4. In date picker i can select one date "Start date" it's highlighted on red but i can apply this even though it suggest an error. Selecting same date as start and end date and apply shows same results. So probably selecting one day should not highlight value to red.
5. Odds filter are exclusive not inclusive (2.9 requirement). Step # 1. Set min 2.09 and max 2.14 - 4 games are present with home odd set to 2.10. Step #2 change min to 2.10 and everything disappears
6. If i type min odd equal to the Home stake then this match is not present on the list. Step #1 - Check the first match on the list and it's home odd (ex. Manchester Utd vs Chelsea, home odd: 2.45) Step #2. Open dropdown for Odds filtering Step #3 set min oodd to the home odd value from step #1 - 2.45) result - match is not visible anymore and so does the others with home stake of value 2.45
7. I can type in lower odd in max than i typed in min
8. Potential payout in pop-up after placing a bet is wrong and not matching the payout presented in Bet Slip (seems like it's always x2 the bet)
9. The team order (home - away) display in pop-up confirmation is replaced by the one shown in the list and in Bet Slip
10. Even after filtering the counter is Showing 103 matches on top.
11. Placing a bet is not decreasing balance live (page needs to be refreshed) and frontend validation allows further betting
12. The balance request in web is cacheable but i would consider it marking not cacheable. It's small value so the cost of it is low but showing the user a proper balance is very important in betting
13. Error popup is disappearing very quickly and user cant place rebet
From requirements:
14. No TIME on the matches list (requirement 2.1)
15. No avail balance in Bet slip when selected a game (remove all is replacing it) - requirement 2.2
16. Header says "Upcoming Football Matches" but past games are also displayed. (requirement 2.1) note here that they are not having any score and that user can still make a bet.
17. I can send a POST request to /api/place-bet with stake value lower than 1 (ex. -1) and get 200 response, body:
{
  "message": "Bet placed successfully",
  "matchId": "premier-league-manutd-chelsea",
  "selection": "HOME",
  "stake": -1,
  "odds": 2.45,
  "payout": -2.46,
  "balance": 43,
  "currency": "USD"
}
18. On above response we see that the currency is invalid (also sent via webui) while doing a bet, probably /api/place-bet should have currency field in request
19. I can place a bets (send requests) even when balance is less than 0
20. Inconsistency in GET https://qae-assignment-tau.vercel.app/api/place-bet is not guarded but GET /api/reset-balance returns error: "method_not_allowed" 
21. User can click multiple times into "Place bet" on UI and this results in placing a lot of bets. During first click a button grayed-out and changed into loading state but still user can spam-click on it. A lot of pop-ups stack then.
22. The error "Something is wrong" is shown for only short period of time while doing steps from #1 and disappear quickly
23. Reset balance set the different value than get_balance
To discuss: API match - id is string and i see posibility to not be unique: "id": "premier-league-manutd-chelsea" but later reponses for matches include the date ex. ligue-1-psg-lyon-2026-04-12 - this requires discussion with team and maybe API documentation update.
Improvement: Add to schema for odds ex. /api/matches (currently numbers) that only positive can be there ("exclusiveminimum": 0) and for OAS3.0 it's a boolean used alongside minimum ("minimum": 0, "exclusiveMinimum": true)
Improvement: "All" button in calendar picker (filtering) is presenting also the calendar in the same time which is misleading - maybe it should hide while selecting this option
Improvement Odds slider does not work when using mouse - UX improvement
Improvement - my stake is cleared each time i select a different bet - would be good to leave the stake typed by the user