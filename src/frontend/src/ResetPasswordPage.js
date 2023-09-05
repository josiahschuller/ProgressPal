import { useState } from "react";
import Avatar from "@mui/material/Avatar";
import CssBaseline from "@mui/material/CssBaseline";

import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";

import LockResetIcon from "@mui/icons-material/LockReset";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import API_URL from "./API_URL";
import Button from "@mui/material/Button";

const theme = createTheme();

export default function ResetPasswordPage() {
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

        // go back to login page
        window.location.href = "/";
      })
      .catch((error) => {
        console.log(error);
      });
  };

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
            Reset Password
          </Typography>
          <Typography component="h1" variant="h6">
            Enter your new password.
          </Typography>
          <TextField id="filled-basic" label="New Password" variant="filled" />
          <Button type="submit" size="large" variant="contained">
            Submit
          </Button>
        </Box>
      </Container>
    </ThemeProvider>
  );
}
