import * as React from "react";
import Box from "@mui/material/Box";
import API_URL from "./API_URL";
import Chart from "chart.js/auto"; // Pick everything. You can hand pick which chartjs features you want, see chartjs docs.
import { Line } from "react-chartjs-2";
import "chartjs-adapter-date-fns";
import ButtonAppBar from "./AppBar";
import { Link } from "react-router-dom";
import { Typography } from "@mui/material";
import HelpIcon from "@mui/icons-material/Help";
import Button from "@mui/material/Button";

function get_activity_impact(goals, activity_id) {
  for (let goal in goals) {
    for (let activity in goals[goal].goal_activities) {
      if (goals[goal].goal_activities[activity].activity_id === activity_id) {
        return goals[goal].goal_activities[activity].activity_impact;
      }
    }
  }
  throw new Error("Activity not found");
}

function get_activity_name(goals, activity_id) {
  for (let goal in goals) {
    for (let activity in goals[goal].goal_activities) {
      if (goals[goal].goal_activities[activity].activity_id === activity_id) {
        return goals[goal].goal_activities[activity].activity_name;
      }
    }
  }
  throw new Error("Activity not found");
}

function get_goal_name(goals, goal_id) {
  let goal_id_int = parseInt(goal_id);
  for (let goal in goals) {
    if (goals[goal].goal_id === goal_id_int) {
      return goals[goal].goal_name;
    }
  }
  throw new Error("Goal not found");
}

function get_most_reported_activities(goals, logs) {
  let activities_sorted_by_frequency = [];
  /*
  Each activity will be an object with the following keys: activity_id, activity_name, frequency
  */
  for (let goalIndex in logs) {
    for (let logIndex in logs[goalIndex].logs) {
      let log = logs[goalIndex].logs[logIndex];
      let activity_id = log.activity_id;
      let activity_frequency = log.activity_frequency;
      let activity_name = get_activity_name(goals, log.activity_id);

      // Check if the activity is already in the list
      let activity_already_in_list = false;
      for (let activityIndex in activities_sorted_by_frequency) {
        if (
          activities_sorted_by_frequency[activityIndex].activity_id ===
          activity_id
        ) {
          // The activity is already in the list
          activity_already_in_list = true;
          activities_sorted_by_frequency[activityIndex].frequency +=
            activity_frequency;
          break;
        }
      }
      if (!activity_already_in_list) {
        // The activity is not in the list
        activities_sorted_by_frequency.push({
          activity_id: activity_id,
          activity_name: activity_name,
          frequency: activity_frequency,
        });
      }
    }
  }

  // Sort the activities by frequency
  activities_sorted_by_frequency.sort((a, b) => {
    return b.frequency - a.frequency;
  });

  return activities_sorted_by_frequency;
}

export default function ReviewPage() {
  // get the goals and corresponding goal progression
  const [goalsLoaded, setGoalsLoaded] = React.useState(false);
  const [goals, setGoals] = React.useState([]);

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

              goalsList.push(goalsResponse[goal]);
            }
            console.log(goalsList);
            setGoals(goalsList);
          }
          setGoalsLoaded(true);
        });
    }
  });

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page="Review" goals={goals} />
      <ReviewContent goals={goals} goalsLoaded={goalsLoaded} />
    </Box>
  );
}

function ReviewContent(props) {
  const { goals, goalsLoaded } = props;

  const [logsLoaded, setLogsLoaded] = React.useState(false);
  const [logs, setLogs] = React.useState([]);

  if (goalsLoaded && !logsLoaded) {
    // Get access token from local storage
    const user_id = localStorage.getItem("user_id");
    const access_token = localStorage.getItem("access_token");

    // Get logged activities
    let url = `${API_URL}/get-logged-activities-for-user`;
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
          setLogs([]);
        } else {
          // Successful response
          let logsResponse = response.success;

          console.log(logsResponse);
          setLogs(logsResponse);
        }
        setLogsLoaded(true);
      });
  }

  return (
    <div>
      <h2 style={{ textAlign: "center", color: "#0D4F48" }}>
        Progression of goals over time
      </h2>
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <LineChart goals={goals} logs={logs} />
      </Box>

      <h2 style={{ textAlign: "center", color: "#0D4F48" }}>
        Most reported activities:
      </h2>
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <Stats goals={goals} logs={logs} />
      </Box>
      <Link to="/help">
        <Box sx={{ position: "fixed", bottom: 5, right: 5 }}>
          <Button variant="outlined" color="success">
            <HelpIcon style={{ color: "#08948c" }} />
            <Typography
              variant="h6"
              component="h2"
              style={{ color: "#08948c" }}
            >
              HELP
            </Typography>
          </Button>
        </Box>
      </Link>
    </div>
  );
}

function LineChart(props) {
  // how to use https://www.educative.io/answers/how-to-use-chartjs-to-create-charts-in-react
  // source: https://www.chartjs.org/docs/latest/charts/line.html#dataset-properties
  const { goals, logs } = props;

  // goals is a list of objects with keys goal_id, goal_name, goal_activities
  //   goal_activities is a list of objects with keys activity_id, activity_name, activity_impact
  // logs is a list of objects with keys goal_id and logs
  //   logs is a list of objects with keys activity_id, activity_date and activity_frequency

  // Intermediate step which I should be building
  // An object with keys goal_id and data
  //   data is a list of objects with keys date and progression_change (sorted in ascending order by date)

  // Once the intermediate step is built, I can build the final step

  // What I want to plot:
  // An object with keys goal_id and data
  //   data is a list of objects with keys date and current_progression (sorted in ascending order by date)

  // Build the intermediate step
  let intermediateStep = {};
  let finalStep = {};
  let data = {};
  // Iterate through each log
  if (goals.length > 0 && logs.length > 0) {
    for (let goal in logs) {
      let goal_id = logs[goal].goal_id;
      let goal_logs = logs[goal].logs;

      let goal_data = [];

      for (let log in goal_logs) {
        let activity_id = goal_logs[log].activity_id;
        // Get the activity impact
        let activity_impact = get_activity_impact(goals, activity_id);

        if (
          !goal_data.find(
            (data_date) => data_date.date === goal_logs[log].activity_date
          )
        ) {
          // There is no log for this goal for this date
          goal_data.push({
            date: goal_logs[log].activity_date,
            progression_change:
              goal_logs[log].activity_frequency * activity_impact,
          });
        } else {
          // There is a log for this goal at this date
          // Find the log for this goal at this date
          let data_date = goal_data.find(
            (data_date) => data_date.date === goal_logs[log].activity_date
          );
          // Get the index of the log for this goal at this date
          let data_date_index = goal_data.indexOf(data_date);
          // Update the progression change
          goal_data[data_date_index].progression_change +=
            goal_logs[log].activity_frequency * activity_impact;
        }

        intermediateStep[goal_id] = goal_data;
      }
    }

    // Build the final step
    // Iterate through each goal
    for (let goal_id of Object.keys(intermediateStep)) {
      let finalData = [];
      let previous_progression = 0;
      for (let data_date of intermediateStep[goal_id]) {
        let date = new Date(data_date.date);
        // Offset the date (to nullify the timezone)
        date.setHours(date.getHours() + date.getTimezoneOffset() / 60)

        finalData.push({
          date: date,
          current_progression:
            previous_progression + data_date.progression_change,
        });
        previous_progression += data_date.progression_change;
      }
      // Sort finalData according to the date
      finalData = finalData.sort((a, b) => a.date - b.date);

      finalStep[goal_id] = finalData;
    }

    data = {
      datasets: Object.entries(finalStep).map(([goal_id, values]) => {
        return {
          label: get_goal_name(goals, goal_id),
          data: values.map(({ date, current_progression }) => ({
            x: date,
            y: current_progression,
          })),
          fill: false,
          tension: 0.1,
        };
      }),
    };

    console.log(data);

    const options = {
      scales: {
        x: {
          type: "time",
          scaleLabel: {
            display: true,
            labelString: "Date",
          },
          time: {
            minUnit: "day",
          },
        },
        y: {
          type: "linear",
          beginAtZero: true,
          scaleLabel: {
            display: true,
            labelString: "Progression towards goal",
          },
        },
      },
      plugins: {
        tooltip: {
          callbacks: {
            title: tooltipItems => {
              let title = tooltipItems[0].parsed.x;
              if (title !== null) {
                title = new Date(title).toDateString();
              }
              return title;
            },
          },
        },          
      }
    };

    return (
      <div style={{ width: "1000px" }}>
        <Line sx={{ borderWidth: 10 }} data={data} options={options} />
      </div>
    );
  } else {
    return (
      <p style={{ color: "#0D4F48" }}>
        Report some activities and come back later to see your progress over
        time!
      </p>
    );
  }
}

function Stats(props) {
  const { goals, logs } = props;

  console.log(goals);
  console.log(logs);

  let mostReportedActivities = [];

  if (goals.length > 0 && logs.length > 0) {
    mostReportedActivities = get_most_reported_activities(goals, logs);
    if (mostReportedActivities.length > 0) {
      console.log(mostReportedActivities);
      return (
        <Box>
          {mostReportedActivities.map((activity, index) => {
            const message = `${index + 1}: ${
              activity.activity_name
            } - reported ${activity.frequency} times\n`;
            return <p key={activity.activity_id}>{message}</p>;
          })}
          <br />
        </Box>
      );
    }
  }
  return (
    <p style={{ color: "#0D4F48" }}>
      Report some activities and come back later to see your most reported
      activities!
    </p>
  );
}
