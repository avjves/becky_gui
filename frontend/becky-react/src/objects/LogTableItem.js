import React from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExclamationTriangle, faInfo, faBug, faQuestion } from '@fortawesome/free-solid-svg-icons';
import FieldText from './FieldText.js';

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

    getLogIcon(level) {
        var icon = null;
        switch(level) {
            case 'ERROR':
                icon = <FontAwesomeIcon icon={faExclamationTriangle} />
                break
            case 'INFO':
                icon = <FontAwesomeIcon icon={faInfo} />
                break
            case 'DEBUG':
                icon = <FontAwesomeIcon icon={faBug} />
                break
            default:
                icon = <FontAwesomeIcon icon={faQuestion} />
                break
        }
        return icon;
    }

    render() {
        console.log(this.props);
        var log = this.props.log;
        var backgroundColor = this.getCardColor(log.level);
        var logIcon = this.getLogIcon(log.level);
        console.log('log', logIcon);
        var itemValues = [['Tag:', log.tag], ['Timestamp:', log.timestamp], ['Message:', log.message]];
        return (
            <div className="border" style={{'backgroundColor': backgroundColor}}>
                <div className="col">
                    <div className="pt-3 pl-4">
                        {logIcon} 
                    </div>
                    <hr />
                </div>
                <div className="col-11 pb-2">
                    <FieldText field='Message' text={log.message} />
                    <FieldText field='Timestamp' text={log.timestamp} />
                    <FieldText field='Tag' text={log.tag} />
                </div>
            </div>
        )
    }


}

export default LogTableItem;
