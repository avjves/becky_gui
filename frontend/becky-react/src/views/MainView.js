import React from "react";
import { Router, Switch, Route, Link, UseRouteMatch, useParams, withRouter } from "react-router-dom";
import history from "../history.js";

import HomeView from './HomeView.js';
import BackupView from './BackupView.js';
import SettingsView from './SettingsView.js';

import Navbar from '../objects/Navbar.js';
import ProgressBar from '../objects/ProgressBar.js';

class MainView extends React.Component {

    constructor(props) {
        super(props);
    }


    render() {
        return (
            <Router history={history}>
                <div id="wrapper">
                    <div id="content-wrapper" className="d-flex flex-column">
                        <div id="content">
                            <Navbar />
                            <div className="container-fluid">
                                <div className="row justify-content-md-center m-2">
                                    <div className="col-8">
                                        <ProgressBar />
                                        <div className="card p-2">
                                            <Switch>
                                                <Route path="/settings">
                                                    <SettingsView />
                                                </Route>
                                                <Route path="/backups">
                                                    <BackupView />
                                                </Route>
                                                <Route path="/">
                                                    <BackupView />
                                                </Route>
                                            </Switch>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </Router>
        );
    }
}

export default MainView;
