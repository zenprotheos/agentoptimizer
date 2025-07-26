# MATCH REPORT SCHEMA TO USE

{
  "match": {
    "match_id": "2025-07-25-COW-vs-DRA", // Unique identifier composed of date and team codes
    "round": 21, // Integer indicating the round of the season
    "date": "2025-07-25", // ISO 8601 format date
    "venue": "Queensland Country Bank Stadium, Townsville", // Full venue name and location
    "kickoff_time": "19:50 AEST", // Local kickoff time with timezone
    "attendance": 22450, // Official crowd attendance figure
    "broadcast": ["Nine", "Fox League", "Kayo"], // TV networks and streaming services covering the match
    "weather": "Clear, 22°C", // Weather conditions at kickoff
    "referees": ["Chris Butler", "Todd Smith"], // Match officials
    "bunker_decisions": 2 // Number of video referee decisions during the match
  },
  "teams": {
    "home": {
      "name": "North Queensland Cowboys", // Full team name
      "score": 26, // Final score
      "halftime_score": 12, // Score at half-time
      "coach": "Todd Payten", // Head coach name
      "captain": "Jason Taumalolo", // Team captain
      "lineup": [
        "1. Scott Drinkwater", // Starting lineup in positional order
        "2. Kyle Feldt",
        "3. Valentine Holmes",
        "4. Peta Hiku",
        // ... etc
      ],
      "interchange": [
        "14. Jake Granville", // Bench players
        "15. Thomas Mikaele",
        "16. Sam McIntyre",
        "17. Kulikefu Finefeuiaki"
        // ... etc
      ]
    },
    "away": {
      "name": "St George Illawarra Dragons", // Full team name
      "score": 18, // Final score
      "halftime_score": 10, // Score at half-time
      "coach": "Shane Flanagan", // Head coach name
      "captain": "Ben Hunt", // Team captain
      "lineup": [
        "1. Tyrell Sloan", // Starting lineup in positional order
        "2. Zac Lomax",
        "3. Moses Suli",
        // ... etc
      ],
      "interchange": [
        "14. Connor Muhleisen", // Bench players
        "15. Ryan Couchman",
        // ... etc
      ]
    }
  },
  "scoring_plays": [
    {
      "team": "North Queensland Cowboys", // Team that scored
      "player": "Valentine Holmes", // Player who scored
      "minute": 15, // Minute of the game when scored
      "type": "try", // Type of score (try, penalty goal, field goal, conversion)
      "description": "Holmes finished off a slick backline move started by Dearden" // Brief description of how the score occurred
    },
    {
      "team": "St George Illawarra Dragons", // Team that scored
      "player": "Zac Lomax", // Player who scored
      "minute": 23, // Minute of the game when scored
      "type": "penalty goal", // Type of score
      "description": "Penalty goal from 35 metres out after high tackle" // Brief description
    }
    // ... more scoring plays
  ],
  "goal_kicking": [
    {
      "player": "Valentine Holmes", // Goal kicker name
      "team": "North Queensland Cowboys", // Team name
      "goals_attempted": 5, // Total conversion and penalty goal attempts
      "goals_successful": 4, // Successful kicks
      "conversion_rate": 0.8 // Success rate as decimal
    },
    {
      "player": "Zac Lomax", // Goal kicker name
      "team": "St George Illawarra Dragons", // Team name
      "goals_attempted": 3, // Total attempts
      "goals_successful": 2, // Successful kicks
      "conversion_rate": 0.67 // Success rate as decimal
    }
  ],
  "key_moments": [
    {
      "minute": 34, // Minute when moment occurred
      "team": "North Queensland Cowboys", // Team involved (if applicable)
      "description": "Dearden's 40/20 kick sets up field position for Cowboys' second try" // Description of the significant moment
    },
    {
      "minute": 68, // Minute when moment occurred
      "team": "St George Illawarra Dragons", // Team involved
      "description": "Hunt's sin bin for professional foul proves costly as Cowboys score next set" // Description of the moment
    }
    // ... more key moments
  ],
  "player_stats": {
    "Scott Drinkwater": {
      "team": "North Queensland Cowboys", // Player's team
      "position": "Fullback", // Playing position
      "minutes_played": 80, // Minutes on field
      "tries": 1, // Tries scored
      "try_assists": 2, // Try assists recorded
      "run_metres": 186, // Metres gained with ball in hand
      "tackles": 8, // Tackles completed
      "tackle_breaks": 3, // Defensive lines broken
      "errors": 0, // Handling errors made
      "line_breaks": 1 // Clean breaks through defensive line
    },
    "Ben Hunt": {
      "team": "St George Illawarra Dragons", // Player's team
      "position": "Halfback", // Playing position
      "minutes_played": 70, // Minutes on field (sin bin time deducted)
      "try_assists": 1, // Try assists recorded
      "kick_metres": 412, // Total kicking metres
      "line_break_assists": 1, // Assists that led to line breaks
      "goals": 0, // Goals kicked
      "forced_dropouts": 1 // Kicks that forced line dropouts
    }
    // ... more player stats
  },
  "match_analysis": {
    "summary": "Cowboys overcame a spirited Dragons outfit 26-18 in Townsville, with Tom Dearden's masterful kicking game and Valentine Holmes' clinical finishing proving the difference.", // Brief match summary
    "turning_point": "Ben Hunt's sin bin in the 68th minute shifted momentum decisively to the Cowboys", // Key moment that changed the game
    "controversies": [
      "Potential knock-on in lead-up to Cowboys' third try not reviewed", // Contentious decisions or incidents
      "Dragons denied penalty try for professional foul in 55th minute"
    ],
    "player_of_the_match": "Tom Dearden", // Best player on ground
    "coach_comments": {
      "Todd Payten": "Really proud of how we controlled the game in the final quarter. Tom's kicking was superb.", // Home coach post-match quote
      "Shane Flanagan": "We competed well but ill-discipline cost us. Can't give away penalties in our own half." // Away coach post-match quote
    }
  },
  "team_stats": {
    "North Queensland Cowboys": {
      "possession_percent": 54, // Percentage of possession during the match
      "completion_rate": 87, // Set completion percentage
      "tackles_made": 298, // Total tackles completed
      "missed_tackles": 24, // Total tackles missed
      "errors": 6, // Total handling errors
      "penalties_conceded": 4 // Total penalties given away
    },
    "St George Illawarra Dragons": {
      "possession_percent": 46, // Percentage of possession during the match
      "completion_rate": 83, // Set completion percentage
      "tackles_made": 315, // Total tackles completed
      "missed_tackles": 28, // Total tackles missed
      "errors": 8, // Total handling errors
      "penalties_conceded": 7 // Total penalties given away
    }
  },
  "media": {
    "highlights_url": "https://nrl.com/highlights/2025/07/25/cowboys-vs-dragons/", // Official highlights video URL
    "match_report_url": "https://nrl.com/news/2025/07/25/cowboys-defeat-dragons-in-townsville/", // Official match report URL
    "photo_gallery_url": "https://nrl.com/photos/2025/07/25/cowboys-dragons-round-21/" // Official photo gallery URL
  }
}