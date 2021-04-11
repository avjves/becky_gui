import React from "react";
import { Router, Switch, Route, Link, UseRouteMatch, useParams, withRouter } from "react-router-dom";
import history from "../history.js";

import HomeView from './HomeView.js';
import BackupView from './BackupView.js';

import Navbar from '../objects/Navbar.js';

class MainView extends React.Component {

    constructor(props) {
        super(props);
    }


    render() {
        console.log(history);
        return (
            <Router history={history}>
                <div id="wrapper">
                    <div id="content-wrapper" className="d-flex flex-column">
                        <div id="content">
                            <Navbar />
                            <div className="container-fluid">
                                <div className="row justify-content-md-center m-2">
                                    <div className="col-8">
                                        <div className="card p-2">
                                            <Switch>
                                                <Route path="/backups">
                                                    <BackupView />
                                                </Route>
                                                <Route path="/">
                                                    <HomeView />
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
