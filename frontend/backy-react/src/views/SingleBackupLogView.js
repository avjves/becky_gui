import React from "react";
import { Button } from 'react-bootstrap';
import axios from 'axios';
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
        }
        this.nextPage = this.nextPage.bind(this);
        this.previousPage = this.previousPage.bind(this);
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


    render() {
        return (
            <div>
                <Header text="Showing logs for a backup:" />
                <LogTable logs={this.state.logs} nextPage={this.nextPage} previousPage={this.previousPage} /> 
            </div>
        );
    }
}

export default withRouter(SingleBackupLogView);
