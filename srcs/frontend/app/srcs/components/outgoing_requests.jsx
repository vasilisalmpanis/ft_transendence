import ftReact              from "../ft_react";
import FriendRequestLayout  from "./friend_request";

let reroute_number = -1;

const OutgoingRequests = (props) => {
	return (
                <ul class="list-group list-group-flush">
					<li className="list-group-item">
						{ (props.requests && props.requests.length > reroute_number)
							?
							<a onClick={() => props.route('/friendrequests/sent')} style={{cursor: "pointer"}}>
								<h5 className="card-title">Sent Requests</h5>
							</a>
							:
							<h5 className="card-title">Sent Requests</h5>
						}
					</li>
					{
						props.requests && props.requests.length
						?
						props.requests.map((request, i) => {
							return (
								<FriendRequestLayout request={request} i={i} setter={props.setter} data={props.requests} sent={props.sent}/>
							);
						})
						: <li className="list-group-item">You sent no friend requests</li>
					}
				</ul>
	);
}

export default OutgoingRequests;