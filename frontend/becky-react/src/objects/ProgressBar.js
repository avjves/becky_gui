import React from 'react';
import axios from 'axios';
import Header from './Header.js';
import { Line } from 'rc-progress';

class ProgressBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            statusMessage: 'Idle',
            percentage: '0',
        }
        this.fetchCurrentStatus = this.fetchCurrentStatus.bind(this);
    }

    componentDidMount() {
        //setInterval(this.fetchCurrentStatus, 1000);
        this.fetchCurrentStatus();
    }

    fetchCurrentStatus() {
        axios.get("http://localhost:6701/api/backups/status/")
        .then((data) => {
            this.setState({
                statusMessage: data.data.status_message,
                percentage: data.data.percentage,
            });

        })
        .catch((err) => {
            this.setState({statusMessage: 'ERROR'});
        });

    }

    render() {
        return (
            <div className="card p-2 mb-3">
                <div className="justify-content-center row">
                    <div className="col-12">
                        <div className="d-table m-auto">
                            <span> {this.state.statusMessage} </span>
                        </div>
                        <Line percent={this.state.percentage}/>
                    </div>
                </div>
            </div>
        );
    }
}

export default ProgressBar;
