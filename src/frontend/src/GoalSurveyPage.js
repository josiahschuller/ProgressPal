import * as React from "react";
import Box from "@mui/material/Box";
import ButtonAppBar from "./AppBar";
import dayjs from "dayjs";
import { DemoContainer } from "@mui/x-date-pickers/internals/demo";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import API_URL from "./API_URL";
import CustomisedSnackbar from "./Snackbar";
import Fab from "@mui/material/Fab";
import HelpIcon from "@mui/icons-material/Help";
import { Typography } from "@mui/material";
import { Link } from "react-router-dom";
import Stack from "@mui/material/Stack";


// icons
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';


const getGoalFromActivityID = (goals, activity_id) => {
  return goals.filter(
    (goal) =>
      goal.activities.filter((activity) => activity.key === activity_id)
        .length > 0
  )[0];
};

const newPickableActivities = (logs, relevant_goal) => {
  // Get the activities that are pickable for a log
  return relevant_goal.activities.filter((activity) => {
    // Filter out activities that have already been logged for the day
    return !logs.some((log) => log.activity === activity.key);
  });
};

// get goals
// get activities for a particular goal based on the selected dates
export default function GoalSurveyPage() {
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
              goalsResponse[goal].key = goalsResponse[goal].goal_id; // Key
              goalsResponse[goal].activities = goalsResponse[
                goal
              ].goal_activities.map((activity) => {
                return {
                  key: activity.activity_id, // Activity key
                  activity_name: activity.activity_name, // Activity name
                };
              });

              goalsList.push(goalsResponse[goal]);
            }
            setGoals(goalsList);
          }
          setGoalsLoaded(true);
        });
    }
  });

  document.body.style.backgroundColor = "#F4FFFE";

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page="Report Activities" goals={goals} />
      <GoalSurveyContent goals={goals} goalsLoaded={goalsLoaded} />
    </Box>
  );
}

function GoalSurveyContent(props) {
  // https://mui.com/x/react-date-pickers/date-field/
  // https://mui.com/system/spacing/

  // Snackbar state
  const [snackbarState, setSnackbarState] = React.useState({
    open: false,
    severity: "info",
    message: "",
  });

  // Snackbar open handler
  const openSnackbar = (severity, message) => {
    setSnackbarState({
      open: true,
      severity: severity,
      message: message,
    });
  };

  const { goals, goalsLoaded } = props;

  // Whether the logs have been loaded from the database or not
  const [logsLoaded, setLogsLoaded] = React.useState(false);

  // Logs are the activities that the user has logged for a particular day with the following keys: key, goal, activity and frequency
  // [
  //   {
  //     key: 0, // Unique key
  //     goal: null, // Goal object
  //     activity: null, // Activity key
  //     frequency: null, // Positive integer
  //   }
  // ]
  //
  const [logs, setLogs] = React.useState([]);

  // The date that the user is currently viewing
  const [date, setDate] = React.useState(dayjs(new Date()));

  // Pickable activities
  // { log_key: [activity1 object, activity2 object, ...] }
  const [pickableActivities, setPickableActivities] = React.useState({ 0: [] });

  const [saveDisabled, setSaveDisabled] = React.useState(true);

  if (goalsLoaded && !logsLoaded) {
    // Get access token from local storage
    const user_id = localStorage.getItem("user_id");
    const access_token = localStorage.getItem("access_token");

    // Get logged activities
    let url = `${API_URL}/get-logged-activities?activity-date=${date
      .toISOString()
      .slice(0, 10)}`;
    fetch(url, {
      headers: {
        "X-User-Id": user_id,
        Authorization: "Bearer " + access_token,
      },
      method: "GET",
    })
      .then((response) => response.json())
      .then((response) => {
        console.log(response);
        if ("error" in response) {
          // If there is an error
          setLogs([]);
        } else {
          // Successful response
          let newPickableActivities = { ...pickableActivities };
          const logsList = response.logs.map((log) => {
            const relevant_goal = getGoalFromActivityID(goals, log.activity_id);

            // Update the pickable activities
            newPickableActivities[log.activity_id.toString()] =
              relevant_goal.activities;

            return {
              ...log,
              key: log.activity_id, // NOTE: The key is not always the activity ID
              goal: relevant_goal,
              activity: log.activity_id,
              date: log.activity_date,
              frequency: log.activity_frequency,
            };
          });
          setLogs(logsList);
          setPickableActivities(newPickableActivities);
        }
        setLogsLoaded(true);
      });
  }

  const handleAdd = () => {
    // Add a new log
    const biggest_key = logs.reduce((acc, cur) => Math.max(acc, cur.key), 0);
    const new_key = biggest_key + 1;
    const newLogs = [
      ...logs,
      {
        key: new_key, // This ensures that no logs have the same key
        goal: null,
        activity: null,
        frequency: 1,
      },
    ];
    setPickableActivities({ ...pickableActivities, new_key: [] });
    setLogs(newLogs);
  };

  const handleDelete = (key) => {
    // Delete a log with the given key

    const deletedLog = logs.filter((log) => log.key === key)[0];

    // Delete the log
    let url = `${API_URL}/delete-logged-activity`;
    const user_id = localStorage.getItem("user_id");
    const access_token = localStorage.getItem("access_token");
    fetch(url, {
      headers: {
        "X-User-Id": user_id,
        Authorization: "Bearer " + access_token,
      },
      method: "DELETE",
      body: JSON.stringify({
        activity_id: deletedLog.activity,
        activity_date: date.toISOString().slice(0, 10),
      }),
    })
      .then((response) => response.status)
      .then((status) => {
        if (status === 200 || status === 400) {
          // Update state
          setLogs(logs.filter((log) => log.key !== key));
          setPickableActivities({ ...pickableActivities, key: [] });

          // Open snackbar
          openSnackbar("success", "Activity log deleted");
        }
      })
      .catch((error) => {
        console.log(error);
        openSnackbar("error", "Activity log not deleted");
      });
  };

  const handleEdit = (key) => (newGoalKey, newActivityKey, newFrequency) => {
    // Edit a log that has a given key
    // Update its goal, activity or frequency
    setLogs(
      logs.map((log) => {
        if (log.key === key) {
          let newLog = { ...log };
          if (newGoalKey != null) {
            // Edit the goal
            newLog.goal = goals.filter((goal) => goal.key === newGoalKey)[0];

            // Update pickable activities
            let newActivities = { ...pickableActivities };
            newActivities[key.toString()] = newPickableActivities(
              logs,
              newLog.goal
            );
            setPickableActivities(newActivities);
          }
          if (newActivityKey != null) {
            // Edit the activity
            newLog.activity = goals
              .filter((goal) => goal.key === newLog.goal.key)[0]
              .activities.filter(
                (activity) => activity.key === newActivityKey
              )[0].key;
          }
          if (newFrequency != null) {
            // Edit the frequency
            newLog.frequency = newFrequency;
          }
          return newLog;
        } else {
          return log;
        }
      })
    );
    // Set save button to enabled
    setSaveDisabled(false);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(logs);

    for (let log in logs) {
      if (logs[log].goal == null) {
        openSnackbar("error", "Goal must be selected");
        return;
      } else if (logs[log].activity == null) {
        openSnackbar("error", "Activity must be selected");
        return;
      } else if (logs[log].frequency <= 0) {
        openSnackbar("error", "Frequency must be positive");
        return;
      }
    }

    // Create query body
    const queryBody = {
      activities_obj: logs.map((log) => [
        log.activity,
        date.toISOString().slice(0, 10),
        parseInt(log.frequency),
      ]),
    };

    // Get access token from local storage
    const user_id = localStorage.getItem("user_id");
    const access_token = localStorage.getItem("access_token");

    // Log activities
    let url = `${API_URL}/edit-logged-activities`;
    fetch(url, {
      headers: {
        "X-User-Id": user_id,
        Authorization: "Bearer " + access_token,
      },
      method: "POST",
      body: JSON.stringify(queryBody),
    })
      .then((response) => response.json())
      .then((response) => {
        console.log(response);
        if ("error" in response) {
          // If there is an error
          openSnackbar("error", response.error);
        } else {
          // Successful response
          openSnackbar("success", "Successfully logged activities");
          setLogsLoaded(false);

          // Set save button to disabled
          setSaveDisabled(true);
        }
      })
      .catch((error) => {
        console.log(error);
        openSnackbar("error", error.error);
      });
  };

  function decreaseDate() {
    // Change the date and reload the logs
    if (saveDisabled) {
      setDate(date.subtract(1, 'day'));
      setLogsLoaded(false);
    } else {
      // If there are unsaved changes, create a warning snackbar to warn the user
      openSnackbar("warning", "You have unsaved changes. Please save or discard them before changing the date.")
    }
  }

  function increaseDate() {
    // Change the date and reload the logs
    if (saveDisabled) {
      setDate(date.add(1, 'day'));
      setLogsLoaded(false);
    } else {
      // If there are unsaved changes, create a warning snackbar to warn the user
      openSnackbar("warning", "You have unsaved changes. Please save or discard them before changing the date.")
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} noValidate>
      <Box display="flex" justifyContent="center">
        <h1 style={{ color: "#0D4F48" }}>
          Report which activities you have completed
        </h1>
        <br />
      </Box>
      <Box display="flex" justifyContent="center">
        <Typography variant="body1">
          This is where you record which activities you have done
          <br/>
          or see activities you have already recorded previously.
          <br/>
          <b>Select a date and start reporting your activities!</b>
        </Typography>
      </Box>
      <Box display="flex" justifyContent="center" m={2}>
        <Stack direction="row">
          <Button style={{ color: "#0D4F48" }} onClick={decreaseDate}>
            <ChevronLeftIcon/>
          </Button>
          <DatePickerValue
            date={date}
            setDate={setDate}
            setLogsLoaded={setLogsLoaded}
            openSnackbar={openSnackbar}
            saveDisabled={saveDisabled}
          />
          <Button style={{ color: "#0D4F48" }} onClick={increaseDate}>
            <ChevronRightIcon/>
          </Button>
        </Stack>
      </Box>
      <Box>
        {logs.map((log) => (
          <LogRow
            log={log}
            goals={goals}
            pickableActivities={pickableActivities[log.key]}
            handleDelete={() => handleDelete(log.key)}
            handleEdit={handleEdit(log.key)}
            key={log.key}
          />
        ))}
      </Box>
      <Fab
        size="medium"
        color="primary"
        aria-label="add"
        onClick={handleAdd}
        sx={{ ml: "290px", mb: 5 }}
        style={{ background: "#08948c" }}
      >
        <AddIcon />
      </Fab>

      <Box justifyContent="center" display="flex">
        <Button
          variant="contained"
          size="large"
          type="submit"
          style={{ background: saveDisabled ? "#e0e0e0" : "#08948c" }}
        >
          Save
        </Button>
      </Box>
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

function DatePickerValue(props) {
  const { date, setDate, setLogsLoaded, openSnackbar, saveDisabled } = props;

  const onChange = (newValue) => {
    // Change the date in the date picker
    if (saveDisabled) {
      setDate(newValue);
      // Tell React state to reload the logs
      setLogsLoaded(false);
    } else {
      // If there are unsaved changes, create a warning snackbar to warn the user
      openSnackbar("warning", "You have unsaved changes. Please save or discard them before changing the date.")
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <DemoContainer components={["DatePicker", "DatePicker"]}>
        <DatePicker
          label="Date (dd/mm/yyyy)"
          value={date}
          onChange={onChange}
          format="DD/MM/YYYY"
        />
      </DemoContainer>
    </LocalizationProvider>
  );
}

function LogRow(props) {
  /*
   * This represents one field of data entry.
   */

  const { goals, pickableActivities, log, handleDelete, handleEdit } = props;

  const frequencyChange = (event) => {
    handleEdit(null, null, event.target.value);
  };

  return (
    <div>
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <br />
        <GoalSelect goals={goals} log={log} handleEdit={handleEdit} />
        <ActivitySelect
          pickableActivities={pickableActivities}
          log={log}
          handleEdit={handleEdit}
        />
        <TextField
          id="outlined-number"
          label="How many times"
          type="number"
          InputLabelProps={{
            shrink: true,
          }}
          style={{ width: "120px" }}
          sx={{ m: 2 }}
          value={log.frequency}
          onChange={frequencyChange}
          inputProps={{ min: 1 }}
        />
        <Button onClick={handleDelete} style={{ color: "#08948c" }}>
          <DeleteIcon fontSize="large" />
        </Button>
      </Box>
    </div>
  );
}

function GoalSelect(props) {
  const { goals, log, handleEdit } = props;

  let initValue = "";
  if (log.goal != null) {
    initValue = log.goal.key;
  }
  const [value, setValue] = React.useState(initValue); // Value of the dropdown menu

  const handleChange = (event) => {
    // Change in the dropdown menu options
    setValue(event.target.value);
    handleEdit(event.target.value, null, null);
  };

  return (
    <FormControl sx={{ maxWidth: "400px", width: "20%", m: 1 }}>
      <InputLabel id="demo-select-small">Goal</InputLabel>
      <Select
        labelId="demo-select-small"
        id="demo-select-small"
        value={value}
        label="Goal"
        onChange={handleChange}
      >
        <MenuItem value="">
          <em></em>
        </MenuItem>
        {goals.map((goal) => (
          // Menu item for each goal
          <MenuItem key={goal.key} value={goal.key}>
            {goal.goal_name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

function ActivitySelect(props) {
  const { pickableActivities, log, handleEdit } = props;

  // If activities are undefined, set it to an empty array
  let activitiesAdjusted = [];
  if (pickableActivities !== undefined) {
    activitiesAdjusted = pickableActivities;
  }

  const handleChange = (event) => {
    // Edit the activity in the log
    handleEdit(null, event.target.value, null);
  };

  return (
    <Box sx={{ maxWidth: "400px", width: "40%", m: 2 }}>
      <FormControl sx={{ width: "100%" }}>
        <InputLabel id="demo-simple-select-label">Activity</InputLabel>
        <Select
          labelId="demo-simple-select-label"
          id="demo-simple-select"
          value={log.activity}
          label="Activity"
          onChange={handleChange}
        >
          {activitiesAdjusted.map((activity) => (
            // Menu item for each activity
            <MenuItem key={activity.key} value={activity.key}>
              {activity.activity_name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
}
