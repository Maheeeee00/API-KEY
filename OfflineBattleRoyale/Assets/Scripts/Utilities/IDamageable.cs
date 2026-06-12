using UnityEngine;

public interface IDamageable
{
    int Health { get; }
    bool IsAlive { get; }
    void TakeDamage(int damage, GameObject attacker);
}
