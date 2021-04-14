import React from "react";
import Button from "@material-ui/core/Button";
import LogTableItem from './LogTableItem.js';

class LogTable extends React.Component {

    render() {
        return (
            <div>
                <div>
                    {this.props.logs.map((log, index) => {
                        return (
                            <div key={index}>
                                <div className="shadow border">
                                    <LogTableItem log={log} />
                                </div>
                                <hr />
                            </div>
                        )
                    })}
                </div>
                <div>
                    <Button variant='contained' className="m-1" color='primary' onClick={this.props.previousPage}> Previous page</Button>
                    <Button variant='contained' className="m-1" color='primary' onClick={this.props.nextPage}> Next page </Button>
                </div>
            </div>
        )
    }

}

export default LogTable;
