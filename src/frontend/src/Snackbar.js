import * as React from 'react';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

export default function CustomisedSnackbar(props) {
    const { state, setState } = props; // Severity should be "error", "warning", "info" or "success"
  
    const closeSnackbar = () => {
        setState({...state,
            open: false
        })
    };
  
    return (
        <Snackbar
            open={state.open}
            autoHideDuration={6000}
            onClose={closeSnackbar}
            anchorOrigin={{ "vertical": "bottom", "horizontal": "center" }}
        >
            <Alert onClose={closeSnackbar} severity={state.severity} sx={{ width: '100%' }}>
            {state.message}
            </Alert>
        </Snackbar>
    );
  }