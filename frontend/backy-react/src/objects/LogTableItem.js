import React from "react";

class LogTableItem extends React.Component {

    render() {
        console.log(this.props);
        var log = this.props.log;
        return (
            <div>
                <p><span>Level: </span>{log.level}</p>
                <p><span>Tag: </span>{log.tag}</p>
                <p><span>Timestamp: </span>{log.timestamp}</p>
                <p><span>Message: </span>{log.message}</p>
            </div>
        )
    }


}

export default LogTableItem;
