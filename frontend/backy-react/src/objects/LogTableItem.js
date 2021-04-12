import React from "react";

class LogTableItem extends React.Component {


    getCardColor(level) {
        var color = null;
        switch(level) {
            case 'INFO':
                color = "rgba(30, 213, 250, 0.1)"
                break;
            case 'DEBUG':
                color = "rgba(239, 250, 30, 0.1)" 
                break;
            case 'ERROR':
                color = "rgba(196, 7, 7, 0.5)"
                break;
            default:
                color = "rgba(0,0,0,0)";
        }
        return color;
    }

    render() {
        console.log(this.props);
        var log = this.props.log;
        var backgroundColor = this.getCardColor(log.level);
        return (
            <div style={{'background-color': backgroundColor}}>
                <p><span>Level: </span>{log.level}</p>
                <p><span>Tag: </span>{log.tag}</p>
                <p><span>Timestamp: </span>{log.timestamp}</p>
                <p><span>Message: </span>{log.message}</p>
            </div>
        )
    }


}

export default LogTableItem;
