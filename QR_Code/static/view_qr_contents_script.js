// qr_contents_script.js
document.addEventListener("DOMContentLoaded", async function() {
    const token = localStorage.getItem("jwt_token");

    if (!token) {
        window.location.href = "/signin";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:5000/user/get_qr_contents", {
            method: "GET",
            headers: {
                "Authorization": `${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();

            if (result.qr_codes && result.qr_codes.length > 0) {
                // Create a table to display the QR codes
                const table = document.createElement("table");
                table.classList.add("qr-contents-table");

                const tableHeader = document.createElement("thead");
                tableHeader.innerHTML = `
                    <tr>
                        <th>ID</th>
                        <th>Content</th>
                    </tr>
                `;
                table.appendChild(tableHeader);

                const tableBody = document.createElement("tbody");

                result.qr_codes.forEach(qr => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${qr.id}</td>
                        <td>${qr.content}</td>
                    `;
                    tableBody.appendChild(row);
                });

                table.appendChild(tableBody);
                document.getElementById("qr-contents").appendChild(table);
            } else {
                document.getElementById("qr-contents").innerHTML = "<p>No QR contents found for this user.</p>";
            }
        } else {
            const error = await response.json();
            document.getElementById("qr-contents").innerHTML = `<p>Error: ${error.error}</p>`;
        }
    } catch (error) {
        console.error("Error fetching QR codes:", error);
        document.getElementById("qr-contents").innerHTML = `<p>Error: Unable to fetch QR codes.</p>`;
    }
});
