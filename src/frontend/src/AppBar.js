import * as React from "react";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

// App bar
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";

// Hamburger menu
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import Divider from "@mui/material/Divider";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import HomeIcon from "@mui/icons-material/Home";
import EditIcon from "@mui/icons-material/Edit";
import SettingsIcon from "@mui/icons-material/Settings";
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted";
import FlagIcon from "@mui/icons-material/Flag";
import PreviewIcon from "@mui/icons-material/Preview";

export default function ButtonAppBar(props) {
  /*
  Reference:
  https://mui.com/material-ui/react-app-bar/
  https://mui.com/material-ui/react-drawer/
  https://mui.com/material-ui/material-icons/
  */

  const { page, goals } = props;

  // Side the hamburger menu appears on
  const anchor = "left";

  // Set the state to initially have the hamburger menu closed
  const [state, setState] = React.useState({
    left: false,
  });

  const GOAL_MENU_ITEMS = goals.map((goal) => ({
    key: goal.key,
    text: goal.goal_name,
    icon: <FlagIcon />,
    href: `/goals/${goal.key}`,
  }));

  const toggleDrawer = (anchor, open) => (event) => {
    if (
      event.type === "keydown" &&
      (event.key === "Tab" || event.key === "Shift")
    ) {
      return;
    }

    setState({ ...state, [anchor]: open });
  };

  // A single menu item
  const menuItem = (key, text, icon, href) => (
    <ListItem key={key} disablePadding>
      <ListItemButton href={href}>
        <ListItemIcon>{icon}</ListItemIcon>
        <ListItemText primary={text} />
      </ListItemButton>
    </ListItem>
  );

  // The hamburger menu
  const hamburgerMenu = (anchor) => (
    <Box
      sx={{ width: 250 }}
      role="presentation"
      onClick={toggleDrawer(anchor, false)}
      onKeyDown={toggleDrawer(anchor, false)}
    >
      <List>
        {menuItem("Home", "Home", <HomeIcon />, "/home")}
        {menuItem("Edit Goals", "Edit Goals", <EditIcon />, "/edit")}
        {menuItem("Report Activities", "Report Activities", <FormatListBulletedIcon />, "/report")}
        {menuItem("Review", "Review", <PreviewIcon />, "/review")}
      </List>
      <Divider />
      <List>
        {GOAL_MENU_ITEMS.map((item) =>
          menuItem(item.key, item.text, item.icon, item.href)
        )}
      </List>
      {/* <Divider />
      <List>
        {menuItem("Settings", "Settings", <SettingsIcon />, "/settings")}
      </List> */}
    </Box>
  );

  return (
    <AppBar position="static" style={{ background: "#08948c" }}>
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
          onClick={toggleDrawer(anchor, true)} // To open the hamburger menu
        >
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {page}
        </Typography>
        <img src={"/favicon.ico"} width={35} height={35} alt="logo" />

        <Button color="inherit" href="/login">
          Logout
        </Button>
        <Drawer
          anchor={anchor}
          open={state[anchor]}
          onClose={toggleDrawer(anchor, false)}
          color="#009688" // To close the hamburger menu
        >
          {hamburgerMenu(anchor)}
        </Drawer>
      </Toolbar>
    </AppBar>
  );
}
