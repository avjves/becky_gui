import React from "react";
import InputLabel from '@material-ui/core/InputLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Typography from "@material-ui/core/Typography";
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

import LocalScanner from '../scanners/LocalScanner.js';

class SingleBackupScannerSettingsView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            scanner: this.props.backup.scanner,
        }

        this.onClickNextButton = this.onClickNextButton.bind(this);
        this.handleChangeScanner = this.handleChangeScanner.bind(this);
    }

    onClickNextButton() {
        this.props.updateBackup({'scanner': this.state.scanner});
    }

    handleChangeScanner(event) {
        this.setState({scanner: event.target.value});
    }
    
    render() {
        return (
            <div>
                <Typography variant="h6"> Filescanner selection: </Typography>
                <Typography variant="h7"> Select a scanner to use for backing up: </Typography>
                <div className="row ml-1">
                    <div className="col-2">
                        <FormControl style={{'width': '100%'}}>
                            <InputLabel htmlFor="age-native-simple">Scanner</InputLabel>
                            <Select native value={this.state.scanner} onChange={this.handleChangeScanner} inputProps={{name: 'scanner'}}>
                                  <option aria-label="None" value="" />
                                  <option value={'local'}>Local scanner</option>
                                  <option value={'local+differential'}>Local differential scanner</option>
                            </Select>
                        </FormControl>
                    </div>
                </div>
                <hr />
                <hr />
                <div className="row ml-auto">
                    <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                        Next
                    </Button>
                </div>
            </div>
        );
    }
}

export default SingleBackupScannerSettingsView;
