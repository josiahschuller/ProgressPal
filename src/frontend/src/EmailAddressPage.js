import { useState } from "react";
import Avatar from "@mui/material/Avatar";
import CssBaseline from "@mui/material/CssBaseline";

import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";

import * as React from "react";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import LockResetIcon from "@mui/icons-material/LockReset";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import API_URL from "./API_URL";
import Button from "@mui/material/Button";

const theme = createTheme();

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default function EmailAddressPage() {
  // these are for snackbar that I got from mui, not sure if it's working cuz can't test without API calls
  // free to make any changes
  const handleClick = () => {
    setOpen(true);
  };

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setOpen(false);
  };
  const handleSubmit = (event) => {
    // Logic for handling a submit button press is here
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    let url = `${API_URL}/reset-password?username=${data.get(
      "username"
    )}&password=${data.get("password")}`;
    fetch(url, {
      method: "POST",
    })
      .then((response) => response.json())
      .then((response) => {
        console.log(response);
        // Set the user ID and access token in the local storage
        localStorage.setItem("user_id", response["user_id"]);
        localStorage.setItem("access_token", response["access_token"]);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const [open, setOpen] = React.useState(false);

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
            gap: 2,
          }}
          onSubmit={handleSubmit}
        >
          <Avatar sx={{ m: 1, bgcolor: "secondary.main" }}>
            <LockResetIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Identify
          </Typography>
          <Typography component="h1" variant="h6">
            Please enter your email address.
          </Typography>
          <Typography component="h1" variant="subtitle1">
            Verification code will be sent to you.
          </Typography>
          <TextField id="filled-basic" label="Email Address" variant="filled" />
          <Button type="submit" size="large" variant="contained">
            Send
          </Button>
          <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
            <Alert
              onClose={handleClose}
              severity="success"
              sx={{ width: "100%" }}
            >
              Email sent! You will get a link shortly if your email address is
              in our database.
            </Alert>
          </Snackbar>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
