import Avatar from "@mui/material/Avatar";
import Button from "@mui/material/Button";
import CssBaseline from "@mui/material/CssBaseline";
import TextField from "@mui/material/TextField";
import { Link } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import API_URL from "./API_URL";
import * as React from "react";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import CustomisedSnackbar from "./Snackbar";

const theme = createTheme();

function validateEmailAddress(emailAddress) {
  // Validate email address
  // Regular expression for validating email addresses
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(emailAddress)) {
    return false;
  }

  if (emailAddress.length === 0 || emailAddress.length > 100) {
    return false;
  }

  return true;
}

export default function LogInPage() {
  const [snackbarState, setSnackbarState] = React.useState({
    open: false,
    severity: "info",
    message: "",
  });

  const [submitDisabled, setSubmitDisabled] = React.useState(true);
  const [emailAddress, setEmailAddress] = React.useState("");
  const [password, setPassword] = React.useState("");

  const changeEmailAddress = (event) => {
    // Change emailAddress
    setEmailAddress(event.target.value);

    // Enable submit button if both fields are filled
    if (validateEmailAddress(event.target.value) && password !== "") {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }

  const changePassword = (event) => {
    // Change password
    setPassword(event.target.value);

    // Enable submit button if both fields are filled
    if (validateEmailAddress(emailAddress) && event.target.value !== "") {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }

  const openSnackbar = (severity, message) => {
    setSnackbarState({
      open: true,
      severity: severity,
      message: message,
    });
  };

  const handleSubmit = (event) => {
    // Logic for handling a submit button press is here
    event.preventDefault();

    if (!validateEmailAddress(emailAddress)) {
      // Open error snackbar
      openSnackbar("error", "Please enter a valid email address");
      return;
    }

    if (password.length === 0) {
      // Open error snackbar
      openSnackbar("error", "Please enter a password");
      return;
    }

    let url = `${API_URL}/log-in?username=${emailAddress}&password=${password}`;
    fetch(url, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((response) => {
        console.log(response);
        if (!("error" in response)) {
          // Set the user ID and access token in the local storage
          localStorage.setItem("user_id", response["user_id"]);
          localStorage.setItem("access_token", response["access_token"]);
          // Go to the home page
          window.location.href = "/home";
        } else {
          // Open error snackbar
          openSnackbar("error", response["error"]);
        }
      })
      .catch((error) => {
        console.log(error);
        // Open error snackbar
        openSnackbar("error", "API connection not working");
      });
  };

  document.body.style.backgroundColor = "#F4FFFE";

  return (
    <ThemeProvider theme={theme}>
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Avatar
            sx={{ m: 1, backgroundColor: "#08948c" }}
          >
            <LockOutlinedIcon />
          </Avatar>

          <Typography component="h1" variant="h5">
            Sign in
          </Typography>
          <p>
            Welcome to <b>ProgressPal</b>. Achieve your goals and improve your
            well-being with our easy-to-use web app. Get inspiration to stay
            motivated and make progress towards your dreams. <b>Sign in</b> and
            get your journey started!
          </p>
          <img src={"favicon.ico"} width={60} height={60} alt="logo" />

          <Box
            component="form"
            onSubmit={handleSubmit}
            noValidate
            sx={{ mt: 1 }}
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="emailAddress"
              label="Email Address"
              name="emailAddress"
              autoComplete="emailAddress"
              autoFocus
              onChange={changeEmailAddress}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              onChange={changePassword}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              style={{ background: submitDisabled ? "#e0e0e0" : "#08948c" }}
              disabled={submitDisabled}
            >
              Sign In
            </Button>
            <Grid container>
              <Grid item>
                <Link to="/signup" variant="body2">
                  {"Don't have an account? Sign Up"}
                </Link>
              </Grid>
            </Grid>
          </Box>
        </Box>
        <CustomisedSnackbar state={snackbarState} setState={setSnackbarState} />
      </Container>
    </ThemeProvider>
  );
}
