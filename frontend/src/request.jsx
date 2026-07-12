import { toast } from "react-toastify";
const BASE_URL = "https://api.hw.io.vn";

export async function request(path, options = {}) {

	const config = {
		method: options.method || "GET",
		headers: {
			"Content-Type": "application/json",
			...(options.headers || {})
		},
		credentials: "include",
		body: options.body ? JSON.stringify(options.body) : undefined
	};

	const res = await fetch(BASE_URL + path, config);

	if (res.status === 429) {
		toast.error("429. Chậm thôi em chai");
		return null;
	}

	// if (!res.ok) {
	// 	const errorText = await res.text();
	// 	throw new Error(`Request failed ${res.status}: ${errorText}`);
	// }
	let data = await res.json()
	console.log(data)
	
	return {
		data: data,
		status: res.status
	};
}


export async function get_request(path, extra = {}) {
	return request(path, {
		method: "GET",
		...extra
	});
}

export async function post_request(path, body = {}, extra = {}) {
	return request(path, {
		method: "POST",
		body: body,
		...extra
	});
}
