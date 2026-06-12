using System;
using UnityEngine;

public class PlayerHealth : MonoBehaviour, IDamageable
{
  [SerializeField] private int maxHealth = 100;
  [SerializeField] private GearLevel helmet = GearLevel.None;
  [SerializeField] private GearLevel vest = GearLevel.None;

  private int currentHealth;

  public int Health => currentHealth;
  public bool IsAlive => currentHealth > 0;
  public GearLevel Helmet => helmet;
  public GearLevel Vest => vest;

  public event Action<int, int> OnHealthChanged;
  public event Action OnDeath;

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
    OnHealthChanged?.Invoke(currentHealth, maxHealth);

    if (!IsAlive)
    {
      OnDeath?.Invoke();
      GameManager.Instance?.RegisterElimination(gameObject, false);
    }
  }

  public void Heal(int amount)
  {
    if (!IsAlive)
    {
      return;
    }

    currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
    OnHealthChanged?.Invoke(currentHealth, maxHealth);
  }

  public void SetHelmet(GearLevel level)
  {
    if (level > helmet)
    {
      helmet = level;
    }
  }

  public void SetVest(GearLevel level)
  {
    if (level > vest)
    {
      vest = level;
    }
  }

  private int ApplyArmorMitigation(int damage)
  {
    float reduction = 0f;
    reduction += GetGearReduction(helmet);
    reduction += GetGearReduction(vest);
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
