import os
import platform
import socket
import subprocess
import qrcode

def get_local_ip():
    """
    Detects the computer's active local network IP address (LAN IP).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connects to an external address without sending packets
        # to determine the primary outbound network interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

def open_file(filepath):
    """
    Opens the generated image in the system's default image viewer.
    """
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", filepath], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", filepath], check=True)
    except Exception:
        pass  # If headless/server environment, ignore

def main():
    # 1. Configuration
    port = 5000  # Default Flask port (change if your app uses a different port)
    local_ip = get_local_ip()
    target_url = f"http://{local_ip}:{port}"
    output_filename = "voting_access_qr.png"

    print("=" * 60)
    print(" KEREVAT NSoE ELECTION - QR CODE GENERATOR")
    print("=" * 60)
    print(f" Detected Local IP : {local_ip}")
    print(f" Target Web URL    : {target_url}")
    print("-" * 60)

    # 2. Configure QR Code Settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    # 3. Print QR code directly in the terminal (scannable from your screen)
    print("\nScan this code from your mobile device connected to the same Wi-Fi:\n")
    qr.print_ascii(invert=True)

    # 4. Save to high-quality PNG image file
    img = qr.make_image(fill_color="#0f172a", back_color="white")  # Navy and white colors
    img.save(output_filename)
    
    print("-" * 60)
    print(f" QR Code image successfully saved as: {os.path.abspath(output_filename)}")
    print(" You can print this image out and place it at voting stations!")
    print("=" * 60)

    # 5. Open image viewer automatically
    open_file(output_filename)

if __name__ == "__main__":
    main()