import React from "react";
import { BrowserRouter as Router, Switch, Route, Link, UseRouteMatch, useParams, withRouter } from "react-router-dom";

import SettingsTable from '../objects/SettingsTable.js';

class SettingsView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            settings: {}
        }
    }

    componentDidMount() {
        this.fetchSettings();
    }

    fetchSettings() {

    }

    saveSettings() {

    }


    render() {
        return (
            <SettingsTable settings={this.state.settings} saveSettings={this.saveSettings} />            
        );
    }
}

export default withRouter(SettingsView);
