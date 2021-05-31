import React from "react";
import { Button } from 'react-bootstrap';
import axios from 'axios';
import { Checkbox, FormControl, FormLabel, FormControlLabel, FormGroup, InputLabel, Input } from "@material-ui/core";
import {  Router, Switch, Route, Link, withRouter } from "react-router-dom";

import history from '../history.js';
import LogTable from '../objects/LogTable.js';
import Header from '../objects/Header.js';

class SingleBackupLogView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            rowsPerPage: 5,
            currentPage: 0,
            logs: [],
            levelsToShow: {'info': true},
        }
        this.nextPage = this.nextPage.bind(this);
        this.previousPage = this.previousPage.bind(this);
        this.onToggleLogLevel = this.onToggleLogLevel.bind(this);
    }

    componentDidMount() {
        this.fetchLogs();
    }

    fetchLogs() {
        axios.get("http://localhost:6701/api/backups/logs/" + this.props.backupId, {
            params: {
                current_page: this.state.currentPage,
                rows_per_page: this.state.rowsPerPage,
                levels_to_show: this.state.levelsToShow,
            }
        })
        .then((data) => {
            this.setState({logs: data.data.logs});
        })
        .catch((err) => {
            console.log("ERROR", err);
        });
    }

    nextPage() {
        if(!(this.state.logs.length < this.state.rowsPerPage)) {
           this.setState({currentPage: this.state.currentPage + 1}, this.fetchLogs);
        }
    }

    previousPage() {
        if(this.state.currentPage > 0) {
            this.setState({currentPage: this.state.currentPage - 1}, this.fetchLogs);
        }
    }


    onToggleLogLevel(event) {
        var level = event.target.name;
        var checked = event.target.checked;
        var currentLevels = this.state.levelsToShow;
        currentLevels[level] = checked;
        this.setState({currentPage: 0, levelsToShow: currentLevels}, this.fetchLogs);
    }


    render() {
        return (
            <div>
                <Header text="Showing logs for a backup:" />
                <hr />
                <FormLabel component="legend">Which log levels to show?</FormLabel>
                <FormGroup row>
                    <FormControlLabel control={<Checkbox defaultChecked={true} onChange={this.onToggleLogLevel} name="info" />} label="Info" />
                    <FormControlLabel control={<Checkbox defaultChecked={false} onChange={this.onToggleLogLevel} name="debug" />} label="Debug" />
                </FormGroup>
                <hr />
                <LogTable logs={this.state.logs} nextPage={this.nextPage} previousPage={this.previousPage} />
            </div>
        );
    }
}

export default withRouter(SingleBackupLogView);
