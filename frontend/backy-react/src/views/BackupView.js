import React from "react";
import { Button } from 'react-bootstrap';
import { Router, Switch, Route, Link, withRouter } from "react-router-dom";

import SingleBackupView from './SingleBackupView.js';
import SingleBackupLogView from './SingleBackupLogView.js';
import BackupListView from './BackupListView.js';

import history from '../history.js';

class BackupView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            backups: [],
            visible: false,
        }
        this.fetchBackups = this.fetchBackups.bind(this);
        this.addNewBackup = this.addNewBackup.bind(this);
    }


    async addNewBackup(backup) {
        fetch("http://localhost:8000/backups/edit/" + backup.id + "/", {
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
            this.setState({backups: data.backups, visible: true});
        })
        .catch((err) => {
            console.log("ERROR", err);
        });

    }


    render() {
        if(this.state.visible) {
            return (
                <React.Fragment>
                    <Router history={history}>
                        <Switch>
                            <Route path={'/backups/edit/:backupId/:stageId'} component={(props) => <SingleBackupView backupId={props.match.params.backupId} stageId={props.match.params.stageId} addNewBackup={this.addNewBackup}/>} />
                            <Route path={'/backups/list'}>
                                <BackupListView backups={this.state.backups}/>
                            </Route>
                            <Route path={'/backups/logs/:backupId'} component={(props) => <SingleBackupLogView backupId={props.match.params.backupId} />} />
                        </Switch>
                    </Router>
                </React.Fragment>
            );
        }
        else {
            return ('')
        }
    }
}

export default BackupView;
