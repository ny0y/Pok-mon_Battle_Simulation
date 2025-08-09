import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

const playy = {
  // Define your API calls here
  getPokemon: async (id) => {
    const response = await axios.get(`${API_URL}/pokemon/${id}`);
    return response.data;
  },
  // Add more API methods as needed
};

export default playy;
