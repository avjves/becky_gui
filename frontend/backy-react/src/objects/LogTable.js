import React from "react";

import LogTableItem from './LogTableItem.js';

class LogTable extends React.Component {

    render() {
        return (
            <div>
                {this.props.logs.map((log, index) => {
                    return (
                        <div index={index} className="card">
                            <LogTableItem log={log} />
                        </div>
                    )
                })}
            </div>
        )
    }

}

export default LogTable;
