import React from "react";
import axios from 'axios';

import SettingsTable from '../objects/SettingsTable.js';

class SettingsView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            settings: []
        }
        this.fetchSettings = this.fetchSettings.bind(this);
        this.saveSettings = this.saveSettings.bind(this);
    }

    componentDidMount() {
        this.fetchSettings();
    }

    fetchSettings() {
        axios.get("http://localhost:8000/settings/", {})
        .then((data) => {
            console.log(data);
            this.setState({settings: data.data.settings});
        })
        .catch((err) => {
            console.log("ERROR", err);
        });

    }

    saveSettings(settings) {
        console.log("saving", settings)
        axios.post("http://localhost:8000/settings/", {
            settings: settings
        })
        .then((data) => {
            this.fetchSettings();
        })
        .catch((err) => {
            console.log("ERROR", err);
        });


    }


    render() {
        return (
            <SettingsTable settings={this.state.settings} saveSettings={this.saveSettings} />            
        );
    }
}

export default SettingsView;
