cd ~/SKG_Portable

echo "✅ Starting SKG Daemon..."
nohup python3 brain/daemon.py > daemon.log 2>&1 &

echo "⚙️  Starting SKG Execution Brain..."
nohup python3 brain/run_skg.py > brain.log 2>&1 &

echo "✅ Starting UI server..."
nohup python3 api.py > /dev/null 2>&1 &

echo "✅ SKG Cockpit running at http://127.0.0.1:5055"

