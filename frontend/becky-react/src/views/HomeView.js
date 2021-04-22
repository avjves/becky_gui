import React from "react";
import { BrowserRouter as Router, Switch, Route, Link, UseRouteMatch, useParams, withRouter } from "react-router-dom";


class HomeView extends React.Component {

    constructor(props) {
        super(props);
    }


    render() {
        return (
            <h2> This is _BACKY_! </h2>
        );
    }
}

export default withRouter(HomeView);
