import * as React from "react";
import API_URL from "./API_URL";
import Box from "@mui/material/Box";
import { useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import IconButton from "@mui/material/IconButton";

import ButtonAppBar from "./AppBar";

export default function HelpPage() {
  // get the goals and corresponding goal progression
  const [goals, setGoals] = React.useState([]);
  const [goalsLoaded, setGoalsLoaded] = React.useState(false);

  React.useEffect(() => {
    if (!goalsLoaded) {
      // Get access token from local storage
      const user_id = localStorage.getItem("user_id");
      const access_token = localStorage.getItem("access_token");

      // Get goals
      let url = `${API_URL}/get-goals`;
      fetch(url, {
        headers: {
          "X-User-Id": user_id,
          Authorization: "Bearer " + access_token,
        },
        method: "GET",
      })
        .then((response) => response.json())
        .then((response) => {
          if ("error" in response) {
            // If there is an error
            setGoals([]);
          } else {
            // Successful response
            let goalsList = [];
            let goalsResponse = JSON.parse(response.goals);
            for (let goal in goalsResponse) {
              goalsResponse[goal].key = goalsResponse[goal].goal_id;
              goalsResponse[goal].activities = goalsResponse[
                goal
              ].goal_activities.map((activity) => {
                return {
                  score: activity.activity_impact,
                  key: activity.activity_id,
                  name: activity.activity_name,
                };
              });

              goalsList.push(goalsResponse[goal]);
            }
            console.log(goalsList);
            setGoals(goalsList);
          }
          setGoalsLoaded(true);
        });
    }
  });

  document.body.style.backgroundColor = "#F4FFFE";

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page="Help" goals={goals} />
      <HelpContent goals={goals} />
    </Box>
  );
}

function HelpContent(props) {
  let navigate = useNavigate();

  return (
    <div>
      <div>
        <IconButton
          color="primary"
          aria-label="upload picture"
          component="label"
          onClick={() => navigate(-1)}
          style={{ margin: 5, color: "#0EB8A7" }}
          size="small"
        >
          <ArrowBackIosNewIcon />
          back
        </IconButton>
      </div>
      <div
        style={{
          marginTop: 0,
          marginBottom: 100,
          marginRight: 100,
          marginLeft: 100,
        }}
      >
        <h1>How can I help? (Q&A)</h1>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>What is my homepage showing?</b>
          <br /> The homepage shows a rose chart that gives you an easy overview
          of your progress towards your goals. Every goal starts at 0 and aims
          to score a 100 on the rose chart. The more coloured the chart is - the
          better your progress is! Different goals are present in different
          colours!
        </ul>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>What is an impact score?</b>
          <br /> Impact score determines how important your activity is to the
          goal you defined. For example, if you believe having a nap will help
          you a lot in achieving your “Improve my sleep schedule” goal, you can
          assign an impact score of 5. Every time you complete this activity -
          take a nap, your goal will progress by 5.
        </ul>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>
            I have accidentally mistyped an activity when defining a goal. Can I
            fix it?
          </b>
          <br /> Yes you can! Head to the navigation bar and select the “Edit
          goals” option. From there, you can select your desired goal and modify
          it.
        </ul>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>How can I improve my progress?</b>
          <br /> Your progress is determined by how many useful activities you
          do. The more helpful activities you specified are done, the quicker
          you will achieve your goals! To tell us what you have done recently,
          you can click on a button below the chart “Report Activities” or head
          to the navigation bar and select "Report Activities" option!
        </ul>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>How to see my goals?</b>
          <br /> You can find all your goals in the navigation bar on the left
          side on your desktop/phone.
        </ul>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>Can I see details of just one goal?</b>
          <br /> Yes you can! Simply head to the navigation bar and select one
          of your goals! You will see their progress and what activities can
          impact it. You can also see any personal notes you have written!
        </ul>
        <ul style={{ marginBottom: 30 }}>
          <b style={{ fontSize: 22 }}>How to find information in the page?</b>
          <br /> Don't worry! We have a helper comment on the concepts that we
          are using.
        </ul>
      </div>
    </div>
  );
}
