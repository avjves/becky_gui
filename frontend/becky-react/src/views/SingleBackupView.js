import React from "react";
import { Button } from 'react-bootstrap';
import {  Router, Switch, Route, Link, withRouter } from "react-router-dom";

import SingleBackupInitialInfoView from './SingleBackupInitialInfoView.js';
import SingleBackupFileSelectionView from './SingleBackupFileSelectionView.js';
import SingleBackupProviderSettingsView from './SingleBackupProviderSettingsView.js';
import SingleBackupScannerSettingsView from './SingleBackupScannerSettingsView.js';

import history from '../history.js';

class SingleBackupView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            backup: {'id': this.props.backupId, 'provider': '', 'providerSettings': {}, 'selections': []},
            maxViewId: 3
        }
        this.updateBackup = this.updateBackup.bind(this);
        this.advanceView = this.advanceView.bind(this);
    }

    componentDidMount() {
        this.fetchBackupData();
    }

    fetchBackupData() {
        if(this.props.backupId != -1) { // Not a new backup
            fetch("http://localhost:6701/backups/backup/" + this.props.backupId, {
                method: 'GET',
                credentials: "include",
            })
            .then((res) => res.json())
            .then((data) => {
                console.log('Backup', data.backup);
                this.setState({backup: data.backup});
            })
            .catch((err) => {
                console.log("ERROR", err);
            });
        }
    }

    updateBackup(updateValues) {
        var currentBackup = this.state.backup;
        for(var key in updateValues) {
            if(updateValues[key] != null) {
               currentBackup[key] = updateValues[key]
            }
        }
        this.setState({backup: currentBackup}, this.advanceView);
    }

    async advanceView() {
        var newViewId = parseInt(this.props.stageId) + 1;
        if(newViewId > this.state.maxViewId) {
            await this.props.addNewBackup(this.state.backup);
            history.push('/backups/list');
        }
        else {
            history.push('/backups/edit/' + this.getBackupId() + '/' + newViewId);
        }

    }

    getBackupId() {
        var splits = this.props.location.pathname.split("/");
        return splits[splits.length-2];
    }

    render() {
        console.log(this.state.backup);
        return (
        <Router history={history}>
            <Switch>
                <Route path="/backups/edit/:backupId/0">
                    <SingleBackupInitialInfoView updateBackup={this.updateBackup} backup={this.state.backup}/>
                </Route>
                <Route path="/backups/edit/:backupId/1">
                    <SingleBackupFileSelectionView updateBackup={this.updateBackup} backup={this.state.backup}/>
                </Route>
                <Route path="/backups/edit/:backupId/2">
                    <SingleBackupScannerSettingsView updateBackup={this.updateBackup} backup={this.state.backup}/>
                </Route>
                <Route path="/backups/edit/:backupId/3">
                    <SingleBackupProviderSettingsView updateBackup={this.updateBackup} backup={this.state.backup}/>
                </Route>
            </Switch>
        </Router>
        );
    }
}

export default withRouter(SingleBackupView);
