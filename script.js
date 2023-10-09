async function searchPlaylists() {
    const searchQuery = document.getElementById("searchQuery").value;

    const response = await fetch("http://localhost:3000/getPlaylist/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            query: searchQuery,
        }),
    });

    if (response.ok) {
        const data = await response.json();
        displayResults(data);
    } else {
        alert("An error occurred while fetching data from the server.");
    }
}

function displayResults(results) {
    const playlistResults = document.getElementById("playlistResults");
    playlistResults.innerHTML = "";

    if (results.error) {
        playlistResults.innerHTML = `<p>${results.error}</p>`;
        return;
    }

    results.forEach((result, index) => {
        const { channel_name, playlist_url, total_view_count } = result;
        const playlistItem = document.createElement("div");
        playlistItem.classList.add("playlist-item");
        playlistItem.innerHTML = `
            <p>Result ${index + 1}</p>
            <p>Channel Name: ${channel_name}</p>
            <p>Total View Count: ${total_view_count}</p>
            <p>Playlist URL: <a href="${playlist_url}" target="_blank">${playlist_url}</a></p>
        `;
        playlistResults.appendChild(playlistItem);
    });
}
