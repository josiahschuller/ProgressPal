import * as React from "react";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import API_URL from "./API_URL";
import CustomisedSnackbar from "./Snackbar";
import { Typography } from "@mui/material";
import HelpIcon from "@mui/icons-material/Help";
import { Link } from "react-router-dom";

// Tabs
import PropTypes from "prop-types";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Stack from "@mui/material/Stack";

// Inside each tab
import TextField from "@mui/material/TextField";
import Fab from "@mui/material/Fab";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import Slider from "@mui/material/Slider";

import ButtonAppBar from "./AppBar";

export default function EditPage() {
  const [goalsLoaded, setGoalsLoaded] = React.useState(false);
  const [goals, setGoals] = React.useState([]);
  const [originalGoalIds, setOriginalGoadIds] = React.useState([]);
  const [originalActivityIds, setOriginalActivityIds] = React.useState([]);

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
            let activityIds = [];

            let goalsList = [];
            let goalsResponse = JSON.parse(response.goals);
            for (let goal in goalsResponse) {
              goalsResponse[goal].key = goalsResponse[goal].goal_id;
              goalsResponse[goal].activities = goalsResponse[
                goal
              ].goal_activities.map((activity) => {
                activityIds.push(activity.activity_id);
                return {
                  score: activity.activity_impact,
                  key: activity.activity_id,
                  name: activity.activity_name,
                };
              });

              goalsList.push(goalsResponse[goal]);
            }
            setOriginalActivityIds(activityIds);
            console.log(goalsList);
            if (goalsList.length === 0) {
              setGoals([{
                key: 0,
                goal_name: "",
                activities: [{ key: 0, name: "", score: 0 }], // Blank activity
                goal_notes: "",
              }])
            } else {
              setGoals(goalsList);
            }
            setOriginalGoadIds(goalsList.map((goal) => goal.key));
          }
          setGoalsLoaded(true);
        });
    }
  });

  document.body.style.backgroundColor = "#F4FFFE";

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page="Edit Goals & Activities" goals={goals.filter(goal => originalGoalIds.includes(goal.key))} />
      <TabGroup
        goals={goals}
        setGoals={setGoals}
        originalGoalIds={originalGoalIds}
        setGoalsLoaded={setGoalsLoaded}
        originalActivityIds={originalActivityIds}
      />
    </Box>
  );
}

function TabGroup(props) {
  /*
  This represents all the tabs
  Reference: https://mui.com/material-ui/react-tabs/
  */

  const [snackbarState, setSnackbarState] = React.useState({
    open: false,
    severity: "info",
    message: "",
  });

  const openSnackbar = (severity, message) => {
    setSnackbarState({
      open: true,
      severity: severity,
      message: message,
    });
  };

  const [tabValue, setTabValue] = React.useState(0);
  const {
    goals,
    setGoals,
    originalGoalIds,
    setGoalsLoaded,
    originalActivityIds,
  } = props;

  const [saveDisabled, setSaveDisabled] = React.useState(true);

  const handleChange = (event, newValue) => {
    // Check if the user has unsaved changes
    if (saveDisabled) {
      // Change tab
      setTabValue(newValue);
      // Disable save button
      setSaveDisabled(true);
    } else {
      // The user has unsaved changes, so open a warning snackbar
      openSnackbar("warning", "You have unsaved changes! Please save or delete the goal before changing tabs.");
    }
  };

  const addBlankGoal = () => {
    // Check if the user has unsaved changes
    if (saveDisabled) {
      // Adds a new goal
      let biggest_key = goals.reduce((acc, cur) => Math.max(acc, cur.key), 0);
      const new_goal = {
        key: biggest_key + 1,
        goal_name: ``,
        activities: [{ key: 0, name: "", score: 0 }], // Blank activity
        goal_notes: "",
      };
      const new_number_of_goals = goals.length + 1;
      setGoals([...goals, new_goal]);
      // Change tab to newly added goal
      setTabValue(new_number_of_goals - 1);
      // Disable save button
      setSaveDisabled(true);
    } else {
      // The user has unsaved changes, so open a warning snackbar
      openSnackbar("warning", "You have unsaved changes! Please save or delete the goal before changing tabs.");
    }
  };

  const deleteGoal = (key) => {
    // Deletes a goal

    // You must always have at least one goal left at the end
    let new_goals = [...goals];
    if (new_goals.length >= 2) {
      // Delete the goal
      let url = `${API_URL}/delete-goal`;
      const access_token = localStorage.getItem("access_token");
      fetch(url, {
        headers: {
          Authorization: "Bearer " + access_token,
        },
        method: "DELETE",
        body: JSON.stringify({ goal_id: key }),
      })
        .then((response) => response.status)
        .then((status) => {
          if (status === 200 || status === 400) {
            // Change tab
            setTabValue(0);

            // Update state
            new_goals = new_goals.filter((goal) => goal.key !== key);
            setGoals(new_goals);

            // Open snackbar
            openSnackbar("success", "Goal deleted");

            // Disable save button
            setSaveDisabled(true);
          }
        })
        .catch((error) => {
          console.log(error);
          openSnackbar("error", "Goal not deleted");
        });
    } else {
      openSnackbar("warning", "You must have at least one goal");
    }
  };

  const changeGoal = (changedGoal, disabled = false) => {
    setGoals(
      goals.map((goal) => {
        if (changedGoal.key === goal.key) {
          // Change the goal
          return changedGoal;
        } else {
          // Leave the goal unchanged
          return goal;
        }
      })
    );
    // Set save button to be enabled (if specified)
    if (disabled === false) {
      setSaveDisabled(disabled);
    }
  };

  const handleSubmit = (event, goalKey) => {
    // isOriginal is a bool saying whether the goal ID already exists
    event.preventDefault();

    const goal = goals.filter((goal) => goal.key === goalKey)[0];

    // Input validation
    if (goal.goal_name.length > 52) {
      // Make sure the goal name is not too long
      openSnackbar("error", "Goal name must be less than 52 characters");
      return;
    }

    if (goal.goal_notes.length > 500) {
      // Make sure the goal notes are not too long
      openSnackbar("error", "Personal notes must be less than 500 characters");
      return;
    }

    if (goal.activities.length === 0) {
      // Make sure there is at least one activity
      openSnackbar("error", "Goal must have at least one activity");
      return;
    }

    for (let activity in goal.activities) {
      // Make sure there are no activities with negative scores
      if (goal.activities[activity].name === "") {
        openSnackbar("error", "Activity name must be provided");
        return;
      } else if (goal.activities[activity].name.length > 52) {
        openSnackbar("error", "Activity name must be less than 52 characters");
        return;
      } else if (goal.activities[activity].score === 0) {
        openSnackbar("error", "Activity impact scores cannot be zero");
        return;
      }
    }

    const queryBody = {
      goal_name: goal.goal_name,
      goal_desc: "",
      goal_activities: goal.activities.map((activity) => {
        // Change activity keys to match backend
        return {
          activity_score: activity.score,
          activity_name: activity.name,
          activity_desc: "",
          activity_id: originalActivityIds.includes(activity.key)
            ? activity.key
            : null,
        };
      }),
      goal_notes: goal.goal_notes,
    };
    const isOriginal = originalGoalIds.filter((id) => id === goalKey).length > 0;

    const user_id = localStorage.getItem("user_id");
    const access_token = localStorage.getItem("access_token");

    let url = "";
    let method = "";
    if (isOriginal) {
      // Edit the goal
      url = `${API_URL}/edit-goal`;
      method = "PUT";
      queryBody["goal_id"] = goalKey;
    } else {
      // Add a new goal
      url = `${API_URL}/add-new-goal`;
      method = "POST";
    }
    console.log(JSON.stringify(queryBody));

    // Make the API call
    fetch(url, {
      headers: {
        "X-User-Id": user_id,
        Authorization: "Bearer " + access_token,
      },
      method: method,
      body: JSON.stringify(queryBody),
    })
      .then((response) => response.json())
      .then((response) => {
        // Successful add/edit
        console.log(response);

        if (response.hasOwnProperty("success")) {
          // Open snackbar
          openSnackbar("success", "Goal saved");

          // Re-get goals
          setGoalsLoaded(false);

          // Set save button to be disabled
          setSaveDisabled(true);
        } else {
          // Open snackbar
          openSnackbar("error", response.error);
        }
      })
      .catch((error) => {
        console.log(error);
        openSnackbar("error", error.error);
      });
  };

  return (
    <Box
      component="form"
      onSubmit={(event) => handleSubmit(event, goals[tabValue].key)}
      noValidate
    >
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Stack direction="row" spacing={2}>
          <Tabs
            value={tabValue}
            onChange={handleChange}
            aria-label="basic tabs example"
            TabIndicatorProps={{ style: { background: "#0EB8A7" } }}
          >
            {goals.map((goal) => (
              <Tab
                key={goal.key}
                label={
                  <span style={{ color: "#08948c" }}>
                    {goal.goal_name !== "" ? goal.goal_name : "New goal"}
                  </span>
                }
                {...a11yProps(0)}
              />
            ))}
          </Tabs>
          <Button
            startIcon={<AddIcon />}
            onClick={addBlankGoal}
            style={{ color: "#08948c" }}
          >
            <Typography
              variant="h6"
              component="h2"
              color="#08948c"
              style={{
                fontSize: 16,
              }}
            >
              Add Goal
            </Typography>
          </Button>
        </Stack>
      </Box>
      {goals.map((goal, index) => (
        <TabContent
          key={goal.key}
          value={tabValue} // The tab which is selected
          index={index}
          goal={goal}
          changeGoal={changeGoal}
          deleteGoal={() => deleteGoal(goal.key)}
          originalActivityIds={originalActivityIds}
          openSnackbar={openSnackbar}
          saveDisabled={saveDisabled}
        />
      ))}
      <CustomisedSnackbar state={snackbarState} setState={setSnackbarState} />
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
    </Box>
  );
}

function TabContent(props) {
  /*
  This represents the content in a single tab.
  Reference:
  https://mui.com/material-ui/react-tabs/
  https://mui.com/system/flexbox/
  https://mui.com/material-ui/react-text-field/
  */
  // value indicates the tab which is selected
  const {
    value,
    index,
    goal,
    changeGoal,
    deleteGoal,
    originalActivityIds,
    openSnackbar,
    saveDisabled,
    ...other
  } = props;

  const changeGoalName = (event) => {
    const newName = event.target.value;
    changeGoal({ ...goal, goal_name: newName });
  };

  const changeGoalNotes = (event) => {
    const newNotes = event.target.value;
    changeGoal({ ...goal, goal_notes: newNotes });
  };

  const addBlankActivity = (score) => {
    // Add new activity to React state
    let new_goal = { ...goal, activities: [...goal.activities] };
    let biggest_key = goal.activities.reduce(
      (acc, cur) => Math.max(acc, cur.key),
      0
    );
    new_goal.activities.push({
      key: biggest_key + 1,
      name: "",
      score: score,
    });
    changeGoal(new_goal, true);
  };

  const changeActivity = (changedActivity) => {
    changeGoal({
      ...goal,
      activities: goal.activities.map((activity) => {
        if (changedActivity.key === activity.key) {
          // Change the goal
          return changedActivity;
        } else {
          // Leave the goal unchanged
          return activity;
        }
      }),
    });
  };

  const deleteActivity = (key) => {
    let new_goal = { ...goal, activities: [...goal.activities] };

    // You must always have at least one activity left at the end
    if (new_goal.activities.length >= 2) {

      // Delete an activity from React state
      new_goal.activities = new_goal.activities.filter(
        (activity) => activity.key !== key
      );

      // Check if key is in originalActivityIds
      if (originalActivityIds.includes(key)) {
        // Delete the activity from the database
        let url = `${API_URL}/delete-activity`;
        const access_token = localStorage.getItem("access_token");
        fetch(url, {
          headers: {
            Authorization: "Bearer " + access_token,
          },
          method: "DELETE",
          body: JSON.stringify({
            activity_id: key,
          }),
        })
          .then((response) => response.status)
          .then((status) => {
            if (status === 200) {
              // Update state
              changeGoal(new_goal, true);

              // Open snackbar
              openSnackbar("success", "Activity deleted");
            } else {
              // Open snackbar
              openSnackbar(
                "error",
                "Unable to delete activity - please try again"
              );
            }
          })
          .catch((error) => {
            console.log(error);
            openSnackbar("error", "Unable to delete activity - please try again");
          });
      } else {
        // Delete the activity from React state
        changeGoal(new_goal, true);

        // Open snackbar
        openSnackbar("success", "Activity deleted");
      }
    } else {
      openSnackbar("warning", "You must have at least one activity");
    }
  };

  function goToReportActivities() {
    // Go to the report activities page
    if (saveDisabled) {
      window.location.href = "/report";
    } else {
      // Open a warning snackbar
      openSnackbar("warning", "You have unsaved changes. Please save or delete the goal before reporting activities.");
    }
  }

  return (
    <div
      role="tabpanel"
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-evenly",
              flexWrap: "wrap",
            }}
          >
            <Box sx={{ width: "10%" }} />
            <Box sx={{ width: "40%" }}>
              <Box sx={{ display: "flex", justifyContent: "center" }}>
                <Stack>
                  <h2>Goal:</h2>

                  <TextField
                    id="goalName"
                    label="Goal Name *"
                    defaultValue={goal.goal_name}
                    name="goalName"
                    onChange={changeGoalName}
                    sx={{ width: "400px" }}
                    autoFocus
                  />
                  <br />
                  <TextField
                    id="notes"
                    label="Personal notes"
                    multiline
                    rows={6}
                    defaultValue={goal.goal_notes}
                    name="notes"
                    onChange={changeGoalNotes}
                  />
                </Stack>
              </Box>
            </Box>

            <Box sx={{ width: "40%" }}>
              <Box>
                <Stack>
                  <h2>Activities:</h2>
                  <Typography variant="body1">
                    <b>Impact score:</b> An activity's <i>impact score</i>{" "}
                    describes how much the activity helps achieve the goal -
                    positive scores for helpful activities and negative scores
                    for unhelpful activities.
                  </Typography>
                  <br />
                  {goal.activities.map((activity) => {
                    return (
                      <Activity
                        activity={activity}
                        key={activity.key}
                        changeActivity={changeActivity}
                        deleteActivity={() => deleteActivity(activity.key)}
                      />
                    );
                  })}
                  <Fab
                    size="medium"
                    color="primary"
                    aria-label="add"
                    onClick={() => addBlankActivity(0)}
                    style={{ background: "#08948c" }}
                  >
                    <AddIcon />
                  </Fab>
                </Stack>
              </Box>
            </Box>
            <Box sx={{ width: "10%" }} />
          </Box>

          <Box sx={{ display: "flex", justifyContent: "center", mt: 5 }}>
            <Stack direction="row">
              <Button
                type="submit"
                variant="contained"
                sx={{ m: 2 }} // Margin
                style={{
                  maxWidth: "500px",
                  minWidth: "200px",
                  background: saveDisabled ? "#e0e0e0" : "#08948c",
                }}
                disabled={saveDisabled}
                name="saveGoal"
              >
                Save Goal
              </Button>
              <Button
                variant="contained"
                sx={{ m: 2 }} // Margin
                style={{
                  maxWidth: "500px",
                  minWidth: "200px",
                }}
                color="error"
                onClick={deleteGoal}
              >
                Delete Goal
              </Button>
              <Button
                variant="contained"
                sx={{ m: 2 }} // Margin
                style={{
                  maxWidth: "500px",
                  minWidth: "200px",
                  background: "#2596be",
                }}
                onClick={goToReportActivities}
              >
                Report Activities
              </Button>
            </Stack>
          </Box>
        </Box>
      )}
    </div>
  );
}

TabContent.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    "aria-controls": `simple-tabpanel-${index}`,
  };
}

function Activity(props) {
  /*
  This represents the text fields for a single activity.
  */

  const {
    activity, // Activity object
    changeActivity, // Function to change an activity
    deleteActivity, // Function to delete an activity
  } = props;

  const changeActivityName = (event) => {
    const newName = event.target.value;
    changeActivity({ ...activity, name: newName });
  };

  const changeActivityScore = (event) => {
    const newScore = event.target.value;
    if (newScore !== null && newScore !== "") {
      changeActivity({ ...activity, score: newScore });
    }
  };

  const max = 10;
  const min = -10;

  const marks = Array.from({ length: max - min + 1 }, (_, index) => ({
    value: index + min,
    label: "",
  })).filter((mark) => mark.value !== 0);

  return (
    <Box sx={{ display: "flex", my: 1, minWidth: "500px" }}>
      <TextField
        id="activityName"
        label="Activity name *"
        defaultValue={activity.name}
        name={`activity${activity.key}`}
        onChange={changeActivityName}
      />
      <Stack>
        <Box sx={{ width: "250px", mx: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography
              sx={{ textAlign: "left" }}
              fontSize="13px"
            >
              Unhelpful
            </Typography>
            <Typography
              sx={{ textAlign: "center" }}
            >
              Impact score
            </Typography>
            <Typography
              sx={{ textAlign: "right" }}
              fontSize="13px"
            >
              Helpful
            </Typography>
          </Box>
          <Slider
            value={activity.score}
            step={null}
            valueLabelDisplay="on"
            marks={marks}
            min={min}
            max={max}
            onChange={changeActivityScore}
          />
        </Box>
      </Stack>

      <Button
        onClick={() => deleteActivity(activity.key)}
        style={{ color: "#08948c" }}
      >
        <DeleteIcon sx={{ mt: 2, mb: 2 }} />
      </Button>
    </Box>
  );
}
