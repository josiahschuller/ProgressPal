import * as React from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import HelpIcon from "@mui/icons-material/Help";

import ButtonAppBar from "./AppBar";

export default function SettingPage() {
  let goals = null;

  if (goals === null) {
    goals = [
      { key: 0, name: "Goal #1", progress: 0.2 },
      { key: 1, name: "Goal #2", progress: 0.5 },
      { key: 2, name: "Goal #3", progress: 0.8 },
    ];
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <ButtonAppBar page="Setting" goals={goals} />
      <SettingContent goals={goals} />
    </Box>
  );
}

function SettingContent(props) {
  const { goals } = props;

  return (
    <div>
      <Box
        sx={{ display: "flex", flexDirection: "column" }}
        alignItems="Center"
        margin="50px"
      >
        <h3>User name: Sudong</h3>
        <h3>Email Address: Sudong</h3>
        <h3>Address: Sudong</h3>
      </Box>
      <Box margin-right="300px" margin-top="500px">
        <Stack
          spacing={20}
          direction="row"
          divider={<Divider orientation="vertical" flexItem />}
          justifyContent="center"
          margin="200px"
        >
          <Button size="large" variant="contained">
            Login & Security
          </Button>
          <Button size="large" variant="contained">
            Accessibility
          </Button>
          <Button size="large" variant="contained">
            Contact Us
          </Button>
        </Stack>
      </Box>
      <Box sx={{ position: "fixed", bottom: 0, right: 0 }}>
        <Button color="primary" sx={{ m: 2 }}>
          <HelpIcon />
          Help
        </Button>
      </Box>
    </div>
  );
}
