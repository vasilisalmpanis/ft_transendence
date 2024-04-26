import ftReact									from "../ft_react";
import { apiClient }							from "../api/api_client";
import {
	C_PROFILE_HEADER,
	C_PROFILE_USERNAME
}												from "../conf/content_en";
import BarLayout								from "../components/barlayout";
import Alert									from "../components/alert";
import Avatar									from "../components/avatar";
import EditIcon									from "../components/edit_icon";
import ClipboardIcon							from "../components/clipboard_icon";
import StatsLayout								from "../components/statslayout";

const ProfileCard = (props) => {
	const [img, setImg] = ftReact.useState(props.data.avatar);
	const [tfa, setTfa] = ftReact.useState("");
	const [error, setError] = ftReact.useState("");
	const [tfaEnabled, setTfaEnabled] = ftReact.useState(localStorage.getItem('2fa') === 'true');
	const updateMe = async () => {
		if (img && img instanceof Blob) {
			const reader = new FileReader();
    		reader.onload = async function(readerEvent) {
				const base64 = readerEvent.target.result;
				const resp = await apiClient.post("/users/me", {"avatar": base64});
				if (resp.error)
					setError(resp.error);
				else
					localStorage.setItem("me", JSON.stringify(resp));
    		};
			reader.readAsDataURL(img);
		}
	}
	return (
		<div className="card justify-content-center" style="width: 18rem;">
			<ul className="list-group list-group-flush">
				<li className="list-group-item">
					<form
						onSubmit={(event)=>{
							event.preventDefault();
							updateMe();
						}}
						className="d-flex flex-column gap-3"
					>
						<div>
						<Avatar img={img}/>
						<h5 className="">{props.data.username}</h5>
						<span
							className="btn translate-middle rounded-pill position-absolute badge rounded-circle bg-primary"
							style={{
								overflow: "hidden",
								top: "75%",
								left: "75%",
							}}
						>
							<EditIcon/>
							<input
								style={{
									position: "absolute",
									top: 0,
									right: 0,
									minWidth: "100%",
									minHeight: "100%",
									filter: "alpha(opacity=0)",
									opacity: 0,
									outline: "none",
									cursor: "inherit",
									display: "block",
								}}
								className="input-control"
								type="file"
								id="imageInput"
								accept="image/*"
								onChange={(event)=>{
    								if (event.target.files[0]) {
										setImg(event.target.files[0]);
    								}
								}}
							/>
						</span>
						</div>
						<button type="submit" className="btn btn-outline-primary">Save</button>
					</form>
				</li>
				<li className="list-group-item">{C_PROFILE_USERNAME}: {props.data.username}</li>
				<li className="list-group-item">
					{
						tfaEnabled
							? <button
								className="btn btn-outline-primary w-100"
								onClick={
									async ()=>{
										const res = await apiClient.delete("/2fa");
										if (res.error)
											setError(res.error)
										else
										{
											localStorage.setItem("2fa", false);
											setTfaEnabled(false);
										}
									}
								}
							>
								Disable 2FA
							</button>
							: <button
								data-bs-toggle="modal"
								data-bs-target="#exampleModal"
								className="btn btn-outline-primary w-100"
								onClick={
									async ()=>{
										const res = await apiClient.post("/2fa");
										if (res.error)
											setError(res.error);
										else if (res.secret) {
											setTfa(res.secret);
										}
									}
								}
							>
								Enable 2FA
							</button>
					}
				</li>
				{error && <Alert msg={error}/>}
			</ul>
			<div
				className="modal fade"
				id="exampleModal"
				tabindex="-1"
				aria-labelledby="exampleModalLabel"
				aria-hidden="true"
			>
  				<div class="modal-dialog modal-dialog-centered">
  					<div className="modal-content">
  						<div className="modal-body">
  							<h3
								className="modal-title fs-5"
								id="exampleModalLabel"
							>
									Add this secret to your authenticator app:
							</h3>
							<button
								type="button"
								className="f-inline-flex align-items-center btn btn-link text-decoration-none"
								onClick={()=>{navigator.clipboard.writeText(tfa)}}
							>
								<span className="me-1 mb-1">{tfa}</span>
								<ClipboardIcon/>
							</button>
							<form
								onSubmit={async (ev)=>{
									ev.preventDefault();
									const code = ev.target[0].value;
									const res = await apiClient.post("/2fa/verify", {"2fa_code": code});
									// console.log('RESPONSE AFTER EVDERYTHING:', res);
									if (res.status === '2FA Verified')
									{
										apiClient.authorize(res);
										localStorage.setItem("2fa", true);
										setTfaEnabled(true);
									}
									else if (res.error)
										setError(res.error);
								}}
								className="d-flex flex-row gap-3 my-3"
							>
								<input
									placeholder={"Code from authenticator app"}
									className="form-control"
									type="number"
									max={999999}
									required
								/>
								<button type="submit" className="btn btn-outline-primary">OK</button>
							</form>
							{error && <Alert msg={error}/>}
  						</div>
  					</div>
  				</div>
			</div>
		</div>
	);
}

const IncomingRequests = (props) => {
	const [incomingRequests, setIncomingRequests] = ftReact.useState(null);
	const [error, setError] = ftReact.useState("");
	ftReact.useEffect(async () => {
		const getIncomingRequests = async () => {
			const data = await apiClient.get(`/friendrequests/incoming`);
			if (data.error)
				setError(data.error);
			else if (data && data.length)
				setIncomingRequests([...data]);
		}
		if (!incomingRequests && !error)
			getIncomingRequests();
	},[incomingRequests]);
	return (
		<div className="card" style="width: 20rem;">
			<ul className="list-group list-group-flush">
				<li className="list-group-item">
					<h5 className="card-title">Friend Requests</h5>
				</li>
				{
					incomingRequests && incomingRequests.length

					? incomingRequests.map((request, i) => {
						return (
							<FriendRequestLayout request={request} i={i} setter={setIncomingRequests} data={incomingRequests}/>
						);
					})
					: <span>Nobody wants to be a friend with you</span>
				}
			</ul>
		</div>
	);

}

const FriendRequestLayout = (props) => {
	const acceptRequest = async () => {
		const data = await apiClient.post(`/friendrequests/accept`, {request_id: props.request.id});
		if (data.error)
			return ;
		else {
			props.setter(null);
		}
	};

	const declineRequest = async () => {
		const data = await apiClient.post(`/friendrequests/decline`, {request_id: props.request.id});
		if (data.error)
			return ;
		else {
			props.setter(props.data.filter((request) => request.id !== props.request.id));
		}
	};
	return (
		<li key={props.i} className="list-group-item d-flex">
				<div className="d-flex flex-row gap-2 my-2 my-lg-0">
					<h5>From:</h5>
					<h5 className="">{props.request.sender.username}</h5>
					<button className="btn btn-success mx-auto" onClick={acceptRequest}>Accept</button>
					<button className="btn btn-danger mx-auto" onClick={declineRequest}>Decline</button>
				</div>
		</li>
	)
}

const Profile = (props) => {
	const me = JSON.parse(localStorage.getItem("me"));
	return (
		<BarLayout route={props.route}>
			{
				me
					? 	<div className="d-grid">
							<div className="row justify-content-center text-center align-items-start g-3">
								<div className="col d-flex justify-content-center">
									<ProfileCard data={me}/>
								</div>
								<div className="col d-flex justify-content-center">
									<StatsLayout user_id={me.id}/>
								</div>
								<div className="col d-flex justify-content-center">
									<IncomingRequests/>
								</div>
							</div>
						</div>
					: 	<button className="spinner-grow" role="status"></button>
			}
		</BarLayout>
	);
}

export default Profile;
