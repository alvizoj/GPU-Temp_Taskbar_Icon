# --------- Imports ---------
import os
import pathlib
import sys
import subprocess
import pkg_resources


# --------- Global Variables ---------
CURRENT_DIRECTORY = pathlib.Path(__file__).parent.absolute()
VBS_FILE_NAME = "launch_GPU_Temp-hidden.vbs"
BATCH_FILE_NAME = "launch_GPU_Temp.bat"


# --------- Helper Functions ---------
def install_dependencies():
    """Check and install required Python packages"""
    print("Checking dependencies...")
    
    required = {'infi.systray', 'Pillow', 'GPUtil'}
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
            print("✓ All dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as error:
            print(f"ERROR: Failed to install dependencies: {error}")
            return False
    else:
        print('✓ All required dependencies are already installed')
        return True


def get_startup_folder():
    """Get the Windows Startup folder path for the current user"""
    startup = os.path.join(
        os.environ['APPDATA'],
        r'Microsoft\Windows\Start Menu\Programs\Startup'
    )
    return startup


def create_vbs_file(destination_folder: str, batch_file_path: pathlib.WindowsPath):
    """Create VBS file at the specified location"""
    vbs_file_path = os.path.join(destination_folder, VBS_FILE_NAME)
    
    # Create VBS file content with absolute path to batch file
    file_content = f'''Set WshShell = CreateObject("WScript.Shell")
    WshShell.Run chr(34) & "{batch_file_path}" & Chr(34), 0
    Set WshShell = Nothing
    '''
    
    try:
        # Write VBS file
        with open(vbs_file_path, 'w') as f:
            f.write(file_content)
        return vbs_file_path
    except Exception as error:
        print(f"ERROR: Failed to create VBS file at {destination_folder}: {error}")
        return None


def create_vbs_launcher(add_to_startup :bool = True):
    """Create VBS file(s) that launch the batch file"""
    
    batch_file_path = CURRENT_DIRECTORY / BATCH_FILE_NAME
    
    # Check if batch file exists
    if not batch_file_path.exists():
        print(f"ERROR: Could not find {batch_file_path}")
        print("Make sure launch_GPU_Temp.bat is in the same folder as this script.")
        return False
    
    success = True
    
    # Always create VBS file in project folder
    print("\nCreating VBS launcher in project folder...")
    local_vbs = create_vbs_file(CURRENT_DIRECTORY, batch_file_path)
    if local_vbs:
        print(f"✓ Local VBS created at: {local_vbs}")
    else:
        success = False
    
    # Optionally create VBS file in Startup folder
    if add_to_startup:
        print("\nCreating VBS launcher in Startup folder...")
        try:
            startup_folder = get_startup_folder()
            startup_vbs = create_vbs_file(startup_folder, batch_file_path)
            if startup_vbs:
                print(f"✓ Startup VBS created at: {startup_vbs}")
                print("[INFO] GPU Temp will now start automatically when you log in to Windows")
            else:
                success = False
        except PermissionError:
            print("ERROR: Permission denied writing to Startup folder.")
            print("Try running this script as administrator.")
            success = False
        except Exception as error:
            print(f"ERROR: Failed to create startup VBS: {error}")
            success = False
    
    return success


def update_batch_file():
    """Ensure batch file uses relative path"""
    batch_file_path = CURRENT_DIRECTORY / BATCH_FILE_NAME
    
    file_content = '''@echo off
    cd /d "%~dp0"
    python GPU_Temp.py
    exit
    '''
    
    try:
        # Check if batch file needs updating
        if batch_file_path.exists():
            with open(batch_file_path, 'r') as f:
                current_content = f.read()
            
            if '%~dp0' not in current_content:
                print("Updating batch file to use relative paths...")
                with open(batch_file_path, 'w') as f:
                    f.write(file_content)
                print("✓ Batch file updated")
        else:
            # Create batch file if it doesn't exist
            print("Creating launch_GPU_Temp.bat...")
            with open(batch_file_path, 'w') as f:
                f.write(file_content)
            print("✓ Batch file created")
        
    except Exception as e:
        print(f"Warning: Could not update batch file: {e}")


# --------- MAIN LOOP ---------
def main():
    print("=" * 60)
    print("GPU Temperature Monitor - Setup Script")
    print("=" * 60)
    print()
    
    # Install dependencies first
    print("Step 1: Installing Dependencies")
    print("-" * 60)
    if not install_dependencies():
        print("\nSetup failed due to dependency installation errors.")
        input("\nPress Enter to exit...")
        return
    
    print("\n" + "=" * 60)
    print("Step 2: Configure Launcher")
    print("-" * 60)
    print("\nThis script will:")
    print("1. Update/create the batch file with relative paths")
    print("2. Create a VBS launcher in the project folder")
    print("3. Optionally add the launcher to Windows Startup folder")
    print()
    
    # Ask to add VBS file to startup folder
    startup_response = input("Add to Windows Startup (auto-start on login)? (Y/n): ").strip().lower()
    add_to_startup = not startup_response or startup_response == 'y'
    
    print("\nInstalling...")
    print("-" * 60)
    
    # Update batch file
    update_batch_file()
    
    # Create VBS launcher(s)
    success = create_vbs_launcher(add_to_startup=add_to_startup)
    
    print("-" * 60)
    
    if success:
        print("\n✓ Setup complete!")
        print("\nTo run GPU Temp manually:")
        print("  - Double-click launch_GPU_Temp-hidden.vbs (no console window)")
        print("  - Or double-click launch_GPU_Temp.bat (with console window)")
        if add_to_startup:
            print("\nGPU Temp will start automatically on next login.")
    
        # Ask if user wants to start application
        print()
        start_now = input("Would you like to start the application now? (Y/n): ").strip().lower()
        if not start_now or start_now == "y":
            print("\nStarting application...")
            vbs_path = CURRENT_DIRECTORY / VBS_FILE_NAME

            try:
                os.startfile(str(vbs_path))
                print("✓ Application started!")
            except Exception as error:
                print(f"ERROR: Could not start application: {error}")
                input("\nPress Enter to exit...")
        else:
            print("\nSetup complete. Run the VBS file when you're ready!")
    
    else:
        print("\nSetup completed with some errors. Check messages above.")


if __name__ == "__main__":
    main()