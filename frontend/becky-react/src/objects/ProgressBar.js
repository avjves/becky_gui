import React from 'react';
import axios from 'axios';
import Header from './Header.js';
import { Line } from 'rc-progress';

class ProgressBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            statusMessage: '',
        }
        this.fetchCurrentStatus = this.fetchCurrentStatus.bind(this);
    }

    componentDidMount() {
        //setInterval(this.fetchCurrentStatus, 50000);
        this.fetchCurrentStatus();
    }

    fetchCurrentStatus() {
        axios.get("http://localhost:8000/backups/status/")
        .then((data) => {
            console.log(data)
            this.setState({statusMessage: data.data.status_message});
        })
        .catch((err) => {
            this.setState({statusMessage: 'ERROR'});
        });

    }

    render() {
        return (
            <div className="card p-2 mb-3">
                <div className="justify-content-center row">
                    <div className="col-3">
                        <Header size="h4"> Current task: </Header>
                    </div>
                    <div className="col-7">
                        <span> {this.state.statusMessage} </span>
                    </div>
                </div>
            </div>
        );
    }
}

export default ProgressBar;
