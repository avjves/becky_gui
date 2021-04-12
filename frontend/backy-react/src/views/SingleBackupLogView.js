import React from "react";
import { Button } from 'react-bootstrap';
import axios from 'axios';
import {  Router, Switch, Route, Link, withRouter } from "react-router-dom";

import history from '../history.js';
import LogTable from '../objects/LogTable.js';

class SingleBackupLogView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            rowsPerPage: 20,
            currentPage: 0,
            logs: [],
        }
    }

    componentDidMount() {
        this.fetchLogs();
    }

    fetchLogs() {
        console.log(this.props)
        axios.get("http://localhost:8000/backups/logs/" + this.props.backupId, {
            params: {
                current_page: this.state.currentPage,
                rows_per_page: this.state.rowsPerPage,
            }
        })
        .then((data) => {
            this.setState({logs: data.data.logs});
        })
        .catch((err) => {
            console.log("ERROR", err);
        });
    }

    render() {
        console.log("LOLOG")
        return (
            <LogTable logs={this.state.logs} nextPage={this.nextPage} previousPage={this.previousPage} /> 
        );
    }
}

export default withRouter(SingleBackupLogView);
