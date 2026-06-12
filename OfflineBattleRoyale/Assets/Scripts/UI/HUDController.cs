using UnityEngine;
using UnityEngine.UI;

public class HUDController : MonoBehaviour
{
  [SerializeField] private Text aliveText;
  [SerializeField] private Slider healthBar;
  [SerializeField] private Text weaponText;
  [SerializeField] private Text ammoText;
  [SerializeField] private Text medkitText;
  [SerializeField] private GameObject victoryPanel;
  [SerializeField] private GameObject defeatPanel;
  [SerializeField] private PlayerHealth playerHealth;
  [SerializeField] private PlayerInventory playerInventory;

  private void OnEnable()
  {
    if (GameManager.Instance != null)
    {
      GameManager.Instance.OnAliveCountChanged += UpdateAliveCount;
      GameManager.Instance.OnMatchEnded += ShowMatchResult;
    }

    if (playerHealth != null)
    {
      playerHealth.OnHealthChanged += UpdateHealth;
    }

    if (playerInventory != null)
    {
      playerInventory.OnInventoryChanged += UpdateInventory;
    }
  }

  private void OnDisable()
  {
    if (GameManager.Instance != null)
    {
      GameManager.Instance.OnAliveCountChanged -= UpdateAliveCount;
      GameManager.Instance.OnMatchEnded -= ShowMatchResult;
    }

    if (playerHealth != null)
    {
      playerHealth.OnHealthChanged -= UpdateHealth;
    }

    if (playerInventory != null)
    {
      playerInventory.OnInventoryChanged -= UpdateInventory;
    }
  }

  private void Start()
  {
    UpdateAliveCount(GameManager.Instance != null ? GameManager.Instance.PlayersAlive : 50);
    UpdateHealth(playerHealth != null ? playerHealth.Health : 100, 100);
    UpdateInventory();
  }

  private void UpdateAliveCount(int count)
  {
    if (aliveText != null)
    {
      aliveText.text = "Alive: " + count;
    }
  }

  private void UpdateHealth(int current, int max)
  {
    if (healthBar != null)
    {
      healthBar.maxValue = max;
      healthBar.value = current;
    }
  }

  private void UpdateInventory()
  {
    if (playerInventory == null)
    {
      return;
    }

    WeaponController weapon = playerInventory.Weapon;
    if (weaponText != null)
    {
      weaponText.text = weapon.Stats != null ? weapon.Stats.displayName : "Unarmed";
    }

    if (ammoText != null)
    {
      ammoText.text = weapon.Stats != null ? weapon.AmmoInMag + " / " + weapon.Stats.magazineSize : "-";
    }

    if (medkitText != null)
    {
      medkitText.text = "Medkits: " + playerInventory.Medkits;
    }
  }

  private void ShowMatchResult(bool playerWon)
  {
    if (victoryPanel != null)
    {
      victoryPanel.SetActive(playerWon);
    }

    if (defeatPanel != null)
    {
      defeatPanel.SetActive(!playerWon);
    }
  }
}
