import React from "react";
import { Button } from 'react-bootstrap';
import { Router, Switch, Route, Link, withRouter } from "react-router-dom";

import SingleBackupView from './SingleBackupView.js';
import BackupListView from './BackupListView.js';

import history from '../history.js';

class BackupView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            backups: []
        }
        this.fetchBackups = this.fetchBackups.bind(this);
        this.addNewBackup = this.addNewBackup.bind(this);
    }


    async addNewBackup(backup) {
        console.log(backup); 
        fetch("http://localhost:8000/backups/" + backup.id + "/", {
            method: 'POST',
            credentials: "include",
            body: JSON.stringify(backup),
        })
        .then((res) => {
            console.log("Saving successful.");
            this.fetchBackups();
        })
        .catch((err) => {
            console.log("ERROR", err);
        });
    }

    componentDidMount() {
        this.fetchBackups();
    }

    fetchBackups() {
        fetch("http://localhost:8000/backups/", {
            method: 'GET',
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log('Backups', data.backups);
            this.setState({backups: data.backups});
        })
        .catch((err) => {
            console.log("ERROR", err);
        });

    }


    render() {
        console.log("PR", this.props)
        return (
            <React.Fragment>
                <Router history={history}>
                    <Switch>
                        <Route path={'/backups/:backupId/:stageId'} component={(props) => <SingleBackupView backupId={props.match.params.backupId} stageId={props.match.params.stageId} addNewBackup={this.addNewBackup}/>} />
                        <Route path={'/backups'}>
                            <BackupListView backups={this.state.backups}/>
                        </Route>
                    </Switch>
                </Router>
            </React.Fragment>
        );
    }
}

export default BackupView;
