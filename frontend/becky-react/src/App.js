import React from "react";

import LoginView from './views/LoginView.js';
import MainView from './views/MainView.js';

import axios from 'axios';

class App extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            csrf: "",
            isAuthenticated: false,
        }
        this.setAuthenticated = this.setAuthenticated.bind(this);
    }

    componentDidMount() {
        this.getSession();
    }

    getCSRF() {
        fetch("http://localhost:8000/api/csrf/", {
            credentials: "include",
        })
        .then((res) => {
            let csrfToken = res.headers.get('X-CSRFToken');
            this.setState({csrf: csrfToken});
            console.log("Current CSRF token: ", csrfToken);
        })
        .catch((err) => {
            console.log("ERROR", err);
        });
    }

    getSession() {
        fetch("http://localhost:8000/api/session/", {
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            if(data.isAuthenticated) {
                this.setState({isAuthenticated: true, visible: true});
            }
            else {
                this.setState({isAuthenticated: false, visible: true});
                this.getCSRF();
            }
        })
        .catch((err) => {
            console.log("ERROR", err);
        });
    }

    setAuthenticated(bool) {
       this.setState({isAuthenticated: bool}); 
    }

    render() {
        if(this.state.visible) {
            if(this.state.isAuthenticated) {
                return (
                    <MainView csrf={this.state.csrf} />
                );
            }
            else {
                return (
                    <LoginView csrf={this.state.csrf} setAuthenticated={this.setAuthenticated} />
                );
            }
        }
        else {
            return (<div />);
        }
    }
}


export default App;