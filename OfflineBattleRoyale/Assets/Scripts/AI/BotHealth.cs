using UnityEngine;

public class BotHealth : MonoBehaviour, IDamageable
{
  [SerializeField] private int maxHealth = 100;
  [SerializeField] private BotInventory inventory;

  private int currentHealth;

  public int Health => currentHealth;
  public bool IsAlive => currentHealth > 0;

  private void Awake()
  {
    currentHealth = maxHealth;
  }

  public void TakeDamage(int damage, GameObject attacker)
  {
    if (!IsAlive)
    {
      return;
    }

    int mitigated = ApplyArmorMitigation(damage);
    currentHealth = Mathf.Max(0, currentHealth - mitigated);

    if (!IsAlive)
    {
      GameManager.Instance?.RegisterElimination(gameObject, true);
      Destroy(gameObject);
    }
  }

  public void Heal(int amount)
  {
    if (!IsAlive)
    {
      return;
    }

    currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
  }

  private int ApplyArmorMitigation(int damage)
  {
    if (inventory == null)
    {
      return damage;
    }

    float reduction = GetGearReduction(inventory.Helmet) + GetGearReduction(inventory.Vest);
    return Mathf.Max(1, Mathf.RoundToInt(damage * (1f - reduction)));
  }

  private static float GetGearReduction(GearLevel level)
  {
    return level switch
    {
      GearLevel.Level1 => 0.1f,
      GearLevel.Level2 => 0.2f,
      GearLevel.Level3 => 0.35f,
      _ => 0f
    };
  }
}
