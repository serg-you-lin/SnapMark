from snapmark.utils.backup_manager import BackupManager
import snapmark as sm   

# sm.restore_backup(r"Examples/Input_multiple", delete_backups=True)   
sm.restore_backup(r"Examples", delete_backups=True, recursive=True)   

